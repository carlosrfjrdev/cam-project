"""
Indicadores técnicos — funções puras sobre barras canônicas (zero I/O).

- ema(values, period): média móvel exponencial (seed = SMA dos primeiros `period`).
- sma(values, period): média móvel aritmética.
- vwap_anchored(bars, anchor): VWAP cumulativa ancorada (daily | weekly), preço
  típico (H+L+C)/3 ponderado por volume; reseta a cada âncora.

Saídas alinhadas ao input (None enquanto não há janela suficiente).
"""
from __future__ import annotations

from collections.abc import Sequence

from cam._shared.research_kernel.bars import Bar


def sma(values: Sequence[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period deve ser > 0")
    out: list[float | None] = [None] * len(values)
    acc = 0.0
    for i, v in enumerate(values):
        acc += v
        if i >= period:
            acc -= values[i - period]
        if i >= period - 1:
            out[i] = acc / period
    return out


def ema(values: Sequence[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period deve ser > 0")
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    k = 2.0 / (period + 1)
    seed = sum(values[:period]) / period  # seed = SMA inicial (convenção comum)
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def _anchor_key(bar: Bar, anchor: str) -> str:
    if anchor == "daily":
        return bar.session_date
    if anchor == "weekly":
        iso = bar.ts_open.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    raise ValueError(f"anchor inválido: {anchor}")


def vwap_anchored(bars: Sequence[Bar], anchor: str = "daily") -> list[float | None]:
    """VWAP cumulativa ancorada. anchor: 'daily' (sessão) ou 'weekly' (semana ISO)."""
    out: list[float | None] = [None] * len(bars)
    cur_key: str | None = None
    cum_pv = 0.0
    cum_v = 0.0
    for i, b in enumerate(bars):
        key = _anchor_key(b, anchor)
        if key != cur_key:
            cur_key = key
            cum_pv = 0.0
            cum_v = 0.0
        typical = (b.high + b.low + b.close) / 3.0
        vol = float(b.volume or 0)
        cum_pv += typical * vol
        cum_v += vol
        out[i] = (cum_pv / cum_v) if cum_v else None
    return out
