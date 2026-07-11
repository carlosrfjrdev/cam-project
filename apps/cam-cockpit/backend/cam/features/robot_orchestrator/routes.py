"""
Router FastAPI da feature `robot_orchestrator` — TASK-U003 (BL-UI-0).

**Read-only.** Expõe um read-model de orquestração para a UI (Robot Orchestrator
Page + Risk Console). Nunca dispara orquestração de ordem (Kevin, Art. 35º).

Fase 0: não há tabela `cam_robots` persistida — o read-model é derivado do
Strategy Registry (`cam_strategies`) + limites vigentes do Risk Engine. A
persistência real de Robots é débito técnico (TD-v0.5-ROBOTS).
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.config import settings
from cam._shared.infra import get_db_session
from cam._shared.risk.limits import get_current_limits
from cam.features.strategies.repository import (
    StrategyNotFoundError,
    StrategyRepository,
)

router = APIRouter(prefix="/api/v1/robots", tags=["robot-orchestrator"])

_repo = StrategyRepository()

# Aderência mínima individual (Art. 11-A item 7).
_ADHERENCE_MIN = 0.95


@router.get("")
async def list_robots(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Lista robôs com estratégias + prioridade (read-model Fase 0).

    Em single-strategy mode (MULTI_STRATEGY_ENABLED=false) cada estratégia ativa
    é apresentada como um robô de prioridade 1.
    """
    rows = await _repo.list_all(session)
    robots = [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "strategies": [
                {
                    "strategy_id": str(r["id"]),
                    "name": r["name"],
                    "priority": 1,
                    "is_active": r["is_active"],
                    "status": r["status"],
                    "suspended": False,
                }
            ],
        }
        for r in rows
    ]
    return {
        "multi_strategy_enabled": settings.multi_strategy_enabled,
        "robots": robots,
    }


@router.get("/{robot_id}/adherence")
async def get_robot_adherence(
    robot_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Aderência individual × agregada (R8.06) + limites vigentes.

    Fase 0: aderência por estratégia ainda não é persistida (vem do journal em
    produção). Retorna estrutura estável com `individual=None` quando ausente.
    """
    try:
        row = await _repo.get(session, robot_id)
    except StrategyNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ROBOT_NOT_FOUND", "id": str(robot_id)},
        ) from err

    limits = get_current_limits()
    return {
        "robot_id": str(robot_id),
        "name": row["name"],
        "individual_adherence": None,
        "aggregate_adherence": None,
        "adherence_min": _ADHERENCE_MIN,
        "suspended": False,
        "limits": {
            "max_win": limits.max_win,
            "max_wdo": limits.max_wdo,
            "source": limits.source,
        },
    }
