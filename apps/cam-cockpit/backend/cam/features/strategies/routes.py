"""
Router FastAPI da feature `strategies` — TASK-U001 (BL-UI-0, SPEC v0.5-COCKPIT-UI).

Expõe o Strategy Registry (v0.4) via HTTP. Read + comandos governados.

Garantias constitucionais (Kevin):
  - **Nenhum endpoint submete ordem** (Art. 35º — IA/UI não envia ordem).
  - `promote` exige EvidencePack (Arts. 28º/29º) salvo RETIRED.
  - `activate` é governado (gate visual no front; aqui apenas troca atômica).

Consome `StrategyRepository` + `PromotionService` v0.4 — sem lógica nova.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session
from cam.features.strategies.domain import StrategyStatus
from cam.features.strategies.promotion import (
    EvidenceRequiredError,
    PromotionService,
)
from cam.features.strategies.repository import (
    InvalidStatusTransitionError,
    StrategyNotFoundError,
    StrategyRepository,
)

router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])

_repo = StrategyRepository()
_promotion = PromotionService(_repo)


class PromoteRequest(BaseModel):
    """Promoção de status. `evidence` ausente só é aceito para RETIRED."""

    target_status: StrategyStatus
    evidence: dict[str, Any] | None = None


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "version": row["version"],
        "asset": row["asset"],
        "author": row["author"],
        "status": row["status"],
        "is_active": row["is_active"],
        "metadata": row.get("metadata_json") or {},
    }


@router.get("")
async def list_strategies(
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, Any]]:
    """Lista todas as estratégias do registry (S1 ORB inclusa quando seedada)."""
    rows = await _repo.list_all(session)
    return [_serialize(r) for r in rows]


@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Busca estratégia por id."""
    try:
        row = await _repo.get(session, strategy_id)
    except StrategyNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STRATEGY_NOT_FOUND", "id": str(strategy_id)},
        ) from err
    return _serialize(row)


@router.post("/{strategy_id}/promote", status_code=status.HTTP_201_CREATED)
async def promote_strategy(
    strategy_id: UUID,
    body: PromoteRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Promove estratégia. Exige EvidencePack salvo RETIRED (Arts. 28º/29º).

    O check de evidência ausente é feito **antes** de tocar o banco — falha
    rápida com `EVIDENCE_REQUIRED` independente de conexão.
    """
    if body.target_status is not StrategyStatus.RETIRED and body.evidence is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "EVIDENCE_REQUIRED",
                "message": (
                    f"Promoção para {body.target_status.value} exige EvidencePack "
                    "(Arts. 28º/29º)."
                ),
            },
        )
    try:
        evidence_pack = _build_evidence(strategy_id, body)
        evidence_id = await _promotion.promote(
            session, strategy_id, body.target_status, evidence_pack
        )
    except EvidenceRequiredError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "EVIDENCE_REQUIRED", "message": str(err)},
        ) from err
    except InvalidStatusTransitionError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "INVALID_TRANSITION", "message": str(err)},
        ) from err
    except StrategyNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STRATEGY_NOT_FOUND", "id": str(strategy_id)},
        ) from err
    return {
        "strategy_id": str(strategy_id),
        "status": body.target_status.value,
        "evidence_id": str(evidence_id),
    }


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Ativa estratégia (troca atômica). NÃO envia ordem — apenas marca ativa."""
    try:
        await _repo.set_active(session, strategy_id)
    except StrategyNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STRATEGY_NOT_FOUND", "id": str(strategy_id)},
        ) from err
    return {"strategy_id": str(strategy_id), "is_active": True}


def _build_evidence(strategy_id: UUID, body: PromoteRequest):  # noqa: ANN202
    """Constrói EvidencePack a partir do payload (ou None para RETIRED)."""
    if body.evidence is None:
        return None
    from decimal import Decimal

    from cam.features.strategies.evidence import EvidencePack

    ev = body.evidence
    return EvidencePack(
        strategy_id=strategy_id,
        status_target=body.target_status,
        backtest_runs=ev.get("backtest_runs", []),
        walk_forward_results=ev.get("walk_forward_results", []),
        paper_results=ev.get("paper_results", []),
        adherence=Decimal(str(ev.get("adherence", "0"))),
        drawdown=Decimal(str(ev.get("drawdown", "0"))),
        expectancy_net=Decimal(str(ev.get("expectancy_net", "0"))),
        custom_metrics=ev.get("custom_metrics", {}),
    )
