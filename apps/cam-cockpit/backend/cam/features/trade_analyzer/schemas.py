"""Schemas Pydantic do Trade Analyzer."""
from __future__ import annotations

from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    provider: str
    model: str
    narrative: str
    metrics: dict
    symbol: str
    tick_summary: dict | None = None
    tick_status: str = "ok"


class LastTickResponse(BaseModel):
    asset: str | None = None
    timestamp: str | None = None
    source: str | None = None
    bridge_online: bool = False
