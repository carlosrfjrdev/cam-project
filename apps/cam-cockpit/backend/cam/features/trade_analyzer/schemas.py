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
    tick_summary: dict | None = None
    tick_status: str = "ok"


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
