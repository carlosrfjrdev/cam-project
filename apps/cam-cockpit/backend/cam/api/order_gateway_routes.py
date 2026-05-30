"""
Order Gateway decisions — TASK-U007 (BL-UI-0, SEC CRÍTICO).

Expõe o ponto mais sensível do sistema **somente para leitura**: o histórico de
decisões do Risk Engine (`cam_risk_decisions`). Cada decisão traz o validator
culpado, o motivo, o ambiente e o ativo/direção.

Garantia constitucional (Kevin, Art. 35º): este router **não tem nenhum verbo
que submeta ordem**. Apenas GET. A submissão de ordem só existe no Order Gateway
de execução, jamais exposta via UI/IA.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session

router = APIRouter(prefix="/api/v1/order-gateway", tags=["order-gateway"])


@router.get("/decisions")
async def list_decisions(
    session: AsyncSession = Depends(get_db_session),
    env: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
) -> list[dict[str, Any]]:
    """
    Lista decisões do Risk Engine (read-only).

    Filtros opcionais: `env` (ambiente) e `decision` (APPROVED/REJECTED).
    REJECTED traz `validator` + `reason` (o culpado).
    """
    clauses: list[str] = []
    params: dict[str, Any] = {"lim": limit}
    if decision is not None:
        clauses.append("decision = :decision")
        params["decision"] = decision.upper()
    if env is not None:
        clauses.append("risk_context->>'env' = :env")
        params["env"] = env
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    result = await session.execute(
        text(
            "SELECT id, order_candidate, risk_context, decision, reason, "
            "       validator, created_at "
            "FROM cam_risk_decisions"
            f"{where} "
            "ORDER BY created_at DESC LIMIT :lim"
        ),
        params,
    )
    return [_serialize(dict(r._mapping)) for r in result.fetchall()]


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("order_candidate") or {}
    ctx = row.get("risk_context") or {}
    return {
        "id": str(row["id"]),
        "decision": row["decision"],
        "validator": row.get("validator"),
        "reason": row.get("reason"),
        "asset": candidate.get("asset"),
        "direction": candidate.get("direction"),
        "contracts": candidate.get("contracts"),
        "env": ctx.get("env"),
        "mode": ctx.get("mode"),
        "created_at": (
            row["created_at"].isoformat() if row.get("created_at") else None
        ),
    }
