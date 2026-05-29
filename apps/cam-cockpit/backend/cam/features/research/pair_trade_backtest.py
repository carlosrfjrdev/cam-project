"""
Pair Trade Backtest — TASK-036 (BL-G SPEC v0.4).

Simulador simples de pair trade (mean reversion sobre spread normalizado).
Sem operação real — apenas research.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from cam.features.research.cross_asset_correlation import (
    CorrelationResult,
    PricePoint,
    compute_correlation,
)


@dataclass
class PairTrade:
    direction: str  # "LONG_A_SHORT_B" | "SHORT_A_LONG_B"
    entry_zscore: float
    entry_index: int
    exit_zscore: float | None = None
    exit_index: int | None = None
    pnl: float = 0.0


@dataclass
class PairBacktestResult:
    asset_a: str
    asset_b: str
    trades: list[PairTrade] = field(default_factory=list)
    correlation: CorrelationResult | None = None
    sharpe: float = 0.0

    @property
    def total_pnl(self) -> float:
        return sum(t.pnl for t in self.trades)


def _rolling_mean_std(
    series: list[float], window: int
) -> tuple[list[float], list[float]]:
    means, stds = [], []
    for i in range(len(series)):
        start = max(0, i - window + 1)
        chunk = series[start : i + 1]
        m = sum(chunk) / len(chunk)
        var = sum((x - m) ** 2 for x in chunk) / len(chunk)
        means.append(m)
        stds.append(math.sqrt(var) if var > 0 else 0.0)
    return means, stds


def run_pair_backtest(
    asset_a: str,
    asset_b: str,
    series_a: Sequence[PricePoint],
    series_b: Sequence[PricePoint],
    *,
    window: int = 30,
    zscore_threshold: float = 2.0,
) -> PairBacktestResult:
    """
    Roda backtest de pair trade. Estratégia simples:
      - Spread = log(price_a) - beta * log(price_b) (beta=1 simplificado).
      - Z-score rolling window dias.
      - Se z > threshold → SHORT spread (SHORT a, LONG b).
      - Se z < -threshold → LONG spread (LONG a, SHORT b).
      - Fecha quando z volta a 0.
    """
    result = PairBacktestResult(asset_a=asset_a, asset_b=asset_b)
    result.correlation = compute_correlation(
        asset_a, asset_b, series_a, series_b, window_days=window,
    )

    # Alinha por timestamp
    ts_set = {p.timestamp for p in series_a} & {p.timestamp for p in series_b}
    sa = sorted(
        [p for p in series_a if p.timestamp in ts_set],
        key=lambda p: p.timestamp,
    )
    sb = sorted(
        [p for p in series_b if p.timestamp in ts_set],
        key=lambda p: p.timestamp,
    )
    if len(sa) < window + 2:
        return result

    spread = [
        math.log(float(sa[i].price)) - math.log(float(sb[i].price))
        for i in range(len(sa))
    ]
    means, stds = _rolling_mean_std(spread, window)
    open_trade: PairTrade | None = None

    pnl_series: list[float] = []
    for i in range(window, len(spread)):
        if stds[i] == 0:
            continue
        z = (spread[i] - means[i]) / stds[i]

        if open_trade is None:
            if z > zscore_threshold:
                open_trade = PairTrade(
                    direction="SHORT_A_LONG_B",
                    entry_zscore=z,
                    entry_index=i,
                )
            elif z < -zscore_threshold:
                open_trade = PairTrade(
                    direction="LONG_A_SHORT_B",
                    entry_zscore=z,
                    entry_index=i,
                )
        else:
            # Fecha quando z cruza 0 na direção contrária
            if (open_trade.direction == "SHORT_A_LONG_B" and z <= 0) or (
                open_trade.direction == "LONG_A_SHORT_B" and z >= 0
            ):
                open_trade.exit_zscore = z
                open_trade.exit_index = i
                # PnL simplificado: variação do spread × direção
                delta = spread[i] - spread[open_trade.entry_index]
                if open_trade.direction == "SHORT_A_LONG_B":
                    open_trade.pnl = -delta
                else:
                    open_trade.pnl = delta
                pnl_series.append(open_trade.pnl)
                result.trades.append(open_trade)
                open_trade = None

    # Sharpe simplificado (mean / std × √252)
    if pnl_series:
        m = sum(pnl_series) / len(pnl_series)
        var = sum((p - m) ** 2 for p in pnl_series) / len(pnl_series)
        sd = math.sqrt(var) if var > 0 else 0.0
        result.sharpe = (m / sd * math.sqrt(252)) if sd > 0 else 0.0
    return result
