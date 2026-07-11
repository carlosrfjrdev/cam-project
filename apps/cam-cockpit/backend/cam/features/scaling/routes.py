"""
Router FastAPI da feature `scaling` — TASK-U004 (BL-UI-0).

Expõe o histórico de escalonamento constitucional (Art. 11-B) para a UI.

Leitura: eventos, elegibilidade vigente, histograma de tentativas bloqueadas
(por critério). Comando: `revoke` (reverte escalonamento → preserva capital,
Art. 6º). **Nunca liga `SCALING_ENABLED` nem envia ordem** (Kevin).

Consome `ScalingEventsRepository` v0.4. `SCALING_ENABLED` permanece false.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.config import settings
from cam._shared.infra import get_db_session
from cam.features.scaling.repository import ScalingEventsRepository

router = APIRouter(prefix="/api/v1/scaling", tags=["scaling"])

_repo = ScalingEventsRepository()

# Critérios de elegibilidade do escalonamento (Art. 11-B).
_CRITERIA = ["PF", "WR", "EXP", "DD", "ADH"]


class RevokeRequest(BaseModel):
    reason: str = "Revogação manual — preservação de capital (Art. 6º)."
    cooldown_days: int = 7


@router.get("/events")
async def list_events(
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=200, le=1000),
) -> list[dict[str, Any]]:
    """Lista eventos de escalonamento (append-only), mais recentes primeiro."""
    result = await session.execute(
        text(
            "SELECT id, ts, event_type, strategy_id, proposed_limit_win, "
            "       proposed_limit_wdo, cooldown_days, cooldown_ends_at, notes "
            "FROM cam_constitutional_scaling_events "
            "ORDER BY ts DESC LIMIT :lim"
        ),
        {"lim": limit},
    )
    return [_serialize_event(dict(r._mapping)) for r in result.fetchall()]


@router.get("/eligibility/{strategy_id}")
async def get_eligibility(
    strategy_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Elegibilidade vigente: escalonamento em vigor (se houver) + flag global."""
    in_force = await _repo.latest_in_force(session, strategy_id)
    return {
        "strategy_id": str(strategy_id),
        "scaling_enabled": settings.scaling_enabled,
        "in_force": _serialize_event(in_force) if in_force else None,
        "criteria": _CRITERIA,
    }


@router.get("/blocked-attempts")
async def blocked_attempts(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Histograma de tentativas bloqueadas por critério (5 critérios Art. 11-B).

    Conta eventos BLOCKED_ATTEMPT agrupados pelo critério violado (lido de
    `notes`/`evidence_json`). Critério não identificado cai em "OTHER".
    """
    result = await session.execute(
        text(
            "SELECT notes, evidence_json "
            "FROM cam_constitutional_scaling_events "
            "WHERE event_type = 'BLOCKED_ATTEMPT'"
        )
    )
    histogram = {c: 0 for c in _CRITERIA}
    histogram["OTHER"] = 0
    for r in result.fetchall():
        m = dict(r._mapping)
        criterion = _extract_criterion(m)
        histogram[criterion] = histogram.get(criterion, 0) + 1
    return {"histogram": histogram, "criteria": _CRITERIA}


@router.post("/revoke/{esc_id}", status_code=status.HTTP_201_CREATED)
async def revoke(
    esc_id: UUID,
    body: RevokeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Revoga um escalonamento em vigor — volta aos limites base (preserva capital).

    Registra evento REVOKED com cooldown. Não é ordem; é redução de risco.
    """
    event_id = await _repo.insert(
        session,
        event_type="REVOKED",
        strategy_id=esc_id,
        cooldown_days=body.cooldown_days,
        notes=body.reason,
    )
    return {
        "event_id": str(event_id),
        "revoked": str(esc_id),
        "cooldown_days": body.cooldown_days,
    }


def _extract_criterion(row: dict[str, Any]) -> str:
    blob = (row.get("notes") or "").upper()
    ev = row.get("evidence_json") or {}
    if isinstance(ev, dict):
        blob += " " + str(ev.get("criterion", "")).upper()
    for c in _CRITERIA:
        if c in blob:
            return c
    return "OTHER"


def _serialize_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "ts": row["ts"].isoformat() if row.get("ts") else None,
        "event_type": row["event_type"],
        "strategy_id": str(row["strategy_id"]) if row.get("strategy_id") else None,
        "proposed_limit_win": row.get("proposed_limit_win"),
        "proposed_limit_wdo": row.get("proposed_limit_wdo"),
        "cooldown_days": row.get("cooldown_days"),
        "cooldown_ends_at": (
            row["cooldown_ends_at"].isoformat()
            if row.get("cooldown_ends_at")
            else None
        ),
        "notes": row.get("notes"),
    }
