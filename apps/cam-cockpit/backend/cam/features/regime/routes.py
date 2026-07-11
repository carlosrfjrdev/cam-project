"""
Rota do overlay de Regime de Markov — ADR-014 / SPEC-Inspetor R-21, R-25.

READ-ONLY (papel A). NÃO emite sinal de execução, NÃO dimensiona posição.
Só para ações (futuros/FIIs → bloco omitido na UI). Lê `cam_inspector_candles`
(populado por /mt5/candles?timeframe=D1).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session
from cam.features.regime import domain
from cam.features.regime.repository import get_close_series
from cam.features.regime.schemas import RegimeResponse

router = APIRouter(prefix="/api/v1", tags=["regime"])


@router.get("/regime/{symbol}", response_model=RegimeResponse)
async def get_regime(
    symbol: str,
    timeframe: str = Query("D1"),
    window: int = Query(20, ge=2, le=200),
    threshold: float = Query(0.05, gt=0, le=0.5),
    session: AsyncSession = Depends(get_db_session),
) -> RegimeResponse:
    sym = symbol.upper()
    params = {"window": window, "threshold": threshold}
    closes = await get_close_series(session, sym, timeframe)

    if len(closes) <= window:
        return RegimeResponse(
            symbol=sym,
            timeframe=timeframe,
            params=params,
            insufficient_data=True,
        )

    result = domain.analyze(closes, window=window, threshold=threshold)
    if result.get("insufficient_data"):
        return RegimeResponse(
            symbol=sym, timeframe=timeframe, params=params, insufficient_data=True
        )

    return RegimeResponse(
        symbol=sym,
        timeframe=timeframe,
        params=params,
        insufficient_data=False,
        current_state=result["current_state"],
        states=result["states"],
        transition_matrix=result["transition_matrix"],
        stationary=result["stationary"],
        signal=result["signal"],
        walk_forward=result["walk_forward"],
    )
