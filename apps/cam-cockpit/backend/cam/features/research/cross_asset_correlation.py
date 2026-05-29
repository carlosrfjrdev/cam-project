"""
Cross-Asset Correlation — TASK-037 (BL-G SPEC v0.4).

Cálculo de correlação rolling entre 2 ativos. Pure Python; sem pandas para
manter import-linter leve (Risk Engine não importa pandas).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class PricePoint:
    timestamp: datetime
    price: Decimal


@dataclass(frozen=True)
class CorrelationResult:
    asset_a: str
    asset_b: str
    correlation: float
    sample_size: int
    window_days: int


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=False))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


def compute_correlation(
    asset_a: str,
    asset_b: str,
    series_a: Sequence[PricePoint],
    series_b: Sequence[PricePoint],
    window_days: int = 30,
) -> CorrelationResult:
    """
    Correlação de Pearson entre returns de duas séries.

    Insuficiência de dados → NaN; caller decide o tratamento.
    """
    cutoff: datetime | None = None
    if series_a and series_b:
        ts_a = max(p.timestamp for p in series_a)
        ts_b = max(p.timestamp for p in series_b)
        cutoff = min(ts_a, ts_b) - timedelta(days=window_days)
        sa = [p for p in series_a if p.timestamp >= cutoff]
        sb = [p for p in series_b if p.timestamp >= cutoff]
    else:
        sa, sb = list(series_a), list(series_b)
    # Alinha por timestamp comum (intersecção)
    ts_set = {p.timestamp for p in sa} & {p.timestamp for p in sb}
    sa = sorted([p for p in sa if p.timestamp in ts_set], key=lambda p: p.timestamp)
    sb = sorted([p for p in sb if p.timestamp in ts_set], key=lambda p: p.timestamp)
    # Returns (log)
    if len(sa) < 2 or len(sb) < 2:
        return CorrelationResult(asset_a, asset_b, float("nan"), 0, window_days)
    ra = [
        math.log(float(sa[i].price) / float(sa[i - 1].price))
        for i in range(1, len(sa))
    ]
    rb = [
        math.log(float(sb[i].price) / float(sb[i - 1].price))
        for i in range(1, len(sb))
    ]
    corr = _pearson(ra, rb)
    return CorrelationResult(asset_a, asset_b, corr, len(ra), window_days)


def is_symmetric(
    r_ab: CorrelationResult, r_ba: CorrelationResult
) -> bool:
    """Correlação é simétrica: a×b ≈ b×a."""
    if math.isnan(r_ab.correlation) or math.isnan(r_ba.correlation):
        return math.isnan(r_ab.correlation) and math.isnan(r_ba.correlation)
    return abs(r_ab.correlation - r_ba.correlation) < 1e-9
