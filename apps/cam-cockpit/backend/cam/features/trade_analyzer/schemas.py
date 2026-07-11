"""Schemas Pydantic do Trade Analyzer."""
from __future__ import annotations

from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    id: int | None = None
    created_at: str | None = None
    provider: str
    model: str
    narrative: str
    metrics: dict
    symbol: str
    enrichment: dict | None = None
    candle_status: str = "none"
    candles_count: int = 0


class HistoryItem(BaseModel):
    id: int
    created_at: str | None = None
    provider: str
    model: str
    symbol: str | None = None
    report_filename: str
    total_trades: int | None = None
    gross_result: float | None = None
    win_rate: float | None = None
    profit_factor: float | None = None


class LastTickResponse(BaseModel):
    asset: str | None = None
    timestamp: str | None = None
    source: str | None = None
    bridge_online: bool = False
