"""
Candles M2 para o Trade Analyzer.

verifica se há candles M2 do papel no range das operações em research_bars;
se faltar, OBTÉM do MT5 (M1 → deriva M2 alinhado à grade) e PERSISTE (upsert).
Reusa o kernel/persistência do Operation Analyzer e do leadlag.
"""
from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import text

from cam._shared.infra import async_session_factory
from cam.features.research.leadlag import repository as research_repo

_log = logging.getLogger("cam.trade_analyzer.candle_data")

_SELECT_M2 = text(
    """
    SELECT extract(epoch FROM ts_open)::bigint AS ts,
           open, high, low, close, volume
    FROM research_bars
    WHERE symbol = :s AND timeframe = 'M2' AND price_series = 'raw'
      AND ts_open >= to_timestamp(:start) AND ts_open <= to_timestamp(:end)
    ORDER BY ts_open ASC
    """
)


async def load_m2(symbol: str, start_epoch: float, end_epoch: float) -> list[dict]:
    async with async_session_factory() as session:
        rows = (
            await session.execute(
                _SELECT_M2,
                {"s": symbol.upper(), "start": start_epoch, "end": end_epoch},
            )
        ).all()
    return [
        {
            "ts": int(r[0]),
            "o": float(r[1]),
            "h": float(r[2]),
            "l": float(r[3]),
            "c": float(r[4]),
            "v": int(r[5] or 0),
        }
        for r in rows
    ]


async def _fetch_and_persist(symbol: str, start_epoch: float) -> int:
    """Best-effort: pagina M1 do MT5 cobrindo até `start`, deriva M2, persiste."""
    try:
        from cam.features.mt5_integration.routes import _service as mt5
        from cam.features.operation_analyzer.chart_service import (
            _derive_multi_session,
            _to_bar,
        )
    except Exception:  # noqa: BLE001
        return 0
    if not mt5.bridge.is_alive():
        return 0

    collected: list[dict] = []
    pos = 0
    for _ in range(12):  # até ~ 12 páginas
        resp = await mt5.get_candles(
            symbol, "M1", 3000, timeout_ms=20000, start_pos=pos
        )
        raw = resp.get("data", {}).get("candles", [])
        if not raw:
            break
        collected = raw + collected
        oldest = min(int(c["ts"]) for c in raw)
        pos += len(raw)
        if oldest <= start_epoch:
            break

    if not collected:
        return 0
    m1 = sorted((_to_bar(symbol, "M1", c) for c in collected), key=lambda b: b.ts_open)
    m2 = _derive_multi_session(m1, "M2")
    rows = [
        {
            "symbol": b.symbol, "timeframe": "M2",
            "ts_open": b.ts_open.timestamp(), "ts_close": b.ts_close.timestamp(),
            "session_date": b.session_date, "open": b.open, "high": b.high,
            "low": b.low, "close": b.close, "volume": b.volume,
            "financial": b.financial, "trades": b.trades, "vwap": b.vwap,
            "is_partial": b.is_partial, "price_series": "raw", "provenance_id": None,
        }
        for b in m2
    ]
    try:
        async with async_session_factory() as session:
            for i in range(0, len(rows), 2000):
                await research_repo.insert_bars(session, rows[i : i + 2000])
            await session.commit()
    except Exception:  # noqa: BLE001
        _log.exception("persist M2 falhou")
        return 0
    return len(rows)


async def ensure_m2(
    symbol: str, start_dt: datetime, end_dt: datetime, min_expected: int = 30
) -> tuple[list[dict], str]:
    """
    Garante candles M2 do range. Retorna (candles, status).
    status: 'db' (já existiam) | 'fetched' (buscados do MT5) | 'partial'/'none'.
    """
    start_e, end_e = start_dt.timestamp(), end_dt.timestamp()
    existing = await load_m2(symbol, start_e, end_e)
    if len(existing) >= min_expected:
        return existing, "db"
    fetched = await _fetch_and_persist(symbol, start_e)
    if fetched:
        reloaded = await load_m2(symbol, start_e, end_e)
        return reloaded, ("fetched" if reloaded else "none")
    return existing, ("partial" if existing else "none")
