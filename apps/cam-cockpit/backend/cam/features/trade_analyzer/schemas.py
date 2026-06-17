"""Schemas Pydantic do Trade Analyzer."""
from __future__ import annotations

from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    provider: str
    model: str
    narrative: str
    metrics: dict
    tick_summary: dict | None = None
