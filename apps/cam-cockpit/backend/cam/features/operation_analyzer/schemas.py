"""Contrato (estável) do Operation Analyzer — preenchido com STUB na casca."""
from __future__ import annotations

from pydantic import BaseModel


class Signal(BaseModel):
    time: str           # horário sugerido da operação
    side: str           # LONG | SHORT
    entry: float
    stop: float
    target: float       # alvo a R:R 1:3
    rr: str = "1:3"
    size: int           # mão sugerida (contratos)
    risk_points: float  # risco em pontos (entry - stop)
    rationale: str


class RiskAnalysis(BaseModel):
    suggested_size: int       # mão analisada
    best_hour: str            # melhor horário identificado
    risk_per_trade: float     # risco por operação (R$)
    max_risk_session: float   # risco máximo da sessão (R$) — informativo
    rr_policy: str = "1:3"
    risk_manager_blocking: bool = False  # sem bloqueios por design


class SignalResponse(BaseModel):
    status: str               # "STUB" enquanto casca
    symbol: str
    strategy: str
    inputs: dict              # o que foi recebido (ticks/candles count)
    risk_analysis: RiskAnalysis
    signals: list[Signal]
    notes: str
