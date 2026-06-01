"""Schemas do overlay de Regime — SPEC-Inspetor §4.5."""
from __future__ import annotations

from pydantic import BaseModel


class WalkForward(BaseModel):
    sharpe: float | None = None
    max_drawdown: float | None = None


class RegimeResponse(BaseModel):
    symbol: str
    timeframe: str
    params: dict
    insufficient_data: bool = False
    current_state: str | None = None
    states: list[str] | None = None
    transition_matrix: list[list[float]] | None = None
    stationary: dict[str, float] | None = None
    signal: float | None = None
    walk_forward: WalkForward | None = None
    disclaimer: str = "histórico, não preditivo"
    attribution: str = (
        "Roan (@RohOnChain) / Lewis Jackson — funções puras vendorizadas"
    )
