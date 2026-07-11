"""
Barras canônicas determinísticas — SPEC v0.5 R-10/R-11/R-12/R-13.

Funções **puras** (zero I/O): a barra canônica é M1; M5…D1 são derivadas por
agregação determinística de M1. Rodar duas vezes produz barras idênticas (R-12).
Bucket ancorado no início da sessão B3 (R-10). Gap overnight preservado (R-13).

ATRIBUIÇÃO de regra (Ada, PROPOSAL §6.1): open=primeiro, high=max, low=min,
close=último, volume/financial/trades=soma; VWAP recomputado (nunca média de
VWAPs); último bucket do dia pode ser is_partial.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

# Minutos por timeframe derivável de M1.
_TF_MINUTES: dict[str, int] = {
    "M1": 1,
    "M2": 2,
    "M5": 5,
    "M10": 10,
    "M15": 15,
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}


@dataclass(frozen=True)
class Bar:
    symbol: str
    timeframe: str
    ts_open: datetime
    ts_close: datetime
    session_date: str  # "YYYY-MM-DD" (session_date, não data corrida — R-13)
    open: float
    high: float
    low: float
    close: float
    volume: int
    trades: int = 0
    financial: float = 0.0
    vwap: float | None = None
    is_partial: bool = False


def timeframe_minutes(tf: str) -> int:
    if tf not in _TF_MINUTES:
        raise ValueError(f"timeframe não suportado: {tf}")
    return _TF_MINUTES[tf]


def _bucket_start(
    ts: datetime, tf_min: int, session_open: datetime
) -> datetime:
    """
    Início do bucket que contém `ts`, ancorado em `session_open` (R-10).
    D1 (1440) → o bucket é a própria sessão (ancorado no open do dia).
    """
    delta_min = int((ts - session_open).total_seconds() // 60)
    if delta_min < 0:
        delta_min = 0
    bucket_index = delta_min // tf_min
    return session_open + timedelta(minutes=bucket_index * tf_min)


def derive(
    m1_bars: list[Bar],
    target_tf: str,
    session_open: datetime,
    session_close: datetime | None = None,
) -> list[Bar]:
    """
    Deriva barras de `target_tf` a partir de M1 (função pura, determinística).

    - `m1_bars`: M1 ordenados de UM símbolo e UMA sessão (mesmo session_date).
    - `session_open`: âncora do bucketing (R-10).
    - `session_close`: se dado, marca is_partial no último bucket incompleto.
    """
    if target_tf == "M1":
        return list(m1_bars)
    if not m1_bars:
        return []
    tf_min = timeframe_minutes(target_tf)
    symbol = m1_bars[0].symbol
    session_date = m1_bars[0].session_date

    # Agrupa M1 por bucket determinístico.
    groups: dict[datetime, list[Bar]] = {}
    for b in sorted(m1_bars, key=lambda x: x.ts_open):
        start = _bucket_start(b.ts_open, tf_min, session_open)
        groups.setdefault(start, []).append(b)

    out: list[Bar] = []
    for start in sorted(groups):
        bucket = groups[start]
        ts_close = start + timedelta(minutes=tf_min)
        volume = sum(b.volume for b in bucket)
        trades = sum(b.trades for b in bucket)
        financial = sum(b.financial for b in bucket)
        # VWAP recomputado do M1 (nunca média de VWAPs) — usa financial/volume
        # quando disponível; senão média ponderada por volume do close.
        vwap: float | None = None
        if financial and volume:
            vwap = financial / volume
        elif volume:
            num = sum(b.close * b.volume for b in bucket)
            vwap = num / volume
        expected = tf_min // timeframe_minutes("M1")
        is_partial = len(bucket) < expected
        if session_close is not None and ts_close > session_close:
            is_partial = True
        out.append(
            Bar(
                symbol=symbol,
                timeframe=target_tf,
                ts_open=start,
                ts_close=ts_close,
                session_date=session_date,
                open=bucket[0].open,
                high=max(b.high for b in bucket),
                low=min(b.low for b in bucket),
                close=bucket[-1].close,
                volume=volume,
                trades=trades,
                financial=financial,
                vwap=vwap,
                is_partial=is_partial,
            )
        )
    return out


def aggressor_from_flags(flags: int) -> int:
    """
    Lado agressor a partir de MqlTick.flags (R-06). +1 comprador, -1 vendedor,
    0 indefinido. Bits: TICK_FLAG_BUY=32, TICK_FLAG_SELL=64 (confirmados no
    PROBE-AGGRESSOR-RESULT.md). BUY e SELL nunca coexistem num trade; se ambos,
    trata como indefinido (defensivo).
    """
    buy = bool(flags & 32)
    sell = bool(flags & 64)
    if buy and not sell:
        return 1
    if sell and not buy:
        return -1
    return 0


def with_adjusted_close(bar: Bar, factor: float) -> Bar:
    """Série ajustada (R-13/§6.3): preço × fator (proventos/splits). Puro."""
    return replace(
        bar,
        open=bar.open * factor,
        high=bar.high * factor,
        low=bar.low * factor,
        close=bar.close * factor,
    )
