"""
TickPersister — persiste ticks ao vivo em `cam_market_ticks` (corpus preditivo).

ADR-014 / SPEC-Inspetor R-07 + critério de aceite 7. Best-effort e **em lote**:
acumula ticks num buffer e faz flush periódico (não um INSERT por tick — protege
o event loop). Falha de banco não derruba o stream (Art. 19 — fail-safe).

Proveniência: `source="mt5.cam_bridge"`. Subscreve `mt5.tick` no bridge.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

_INSERT = text(
    """
    INSERT INTO cam_market_ticks (asset, price, volume, timestamp, source)
    VALUES (:asset, :price, :volume, to_timestamp(:ts_s), :source)
    """
)

_FLUSH_INTERVAL_S = 1.0
_MAX_BUFFER = 500


class TickPersister:
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        self._factory = session_factory
        self._buffer: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self._stop = False

    async def on_tick(self, payload: bytes) -> None:
        """Handler do bridge para `mt5.tick`. Normaliza e enfileira."""
        try:
            data = json.loads(payload.decode("utf-8", errors="replace"))
        except (ValueError, AttributeError):
            return
        symbol = str(data.get("symbol", "")).strip().upper()[:10]
        if not symbol:
            return
        last = data.get("last") or 0
        if not last:
            bid = data.get("bid") or 0
            ask = data.get("ask") or 0
            last = (bid + ask) / 2 if (bid and ask) else (bid or ask)
        if not last:
            return
        ts_ms = data.get("ts_unix_ms") or 0
        row = {
            "asset": symbol,
            "price": round(float(last), 2),
            "volume": int(data.get("volume") or 0),
            "ts_s": (ts_ms / 1000.0) if ts_ms else None,
            "source": "mt5.cam_bridge",
        }
        if row["ts_s"] is None:
            return
        async with self._lock:
            if len(self._buffer) < _MAX_BUFFER:
                self._buffer.append(row)

    async def _flush(self) -> None:
        async with self._lock:
            if not self._buffer:
                return
            rows = self._buffer[:]
            self._buffer.clear()
        try:
            async with self._factory() as session:
                await session.execute(_INSERT, rows)
                await session.commit()
        except Exception:
            # corpus é best-effort — não propaga (Art. 19)
            pass

    async def _flush_loop(self) -> None:
        try:
            while not self._stop:
                await asyncio.sleep(_FLUSH_INTERVAL_S)
                await self._flush()
        except asyncio.CancelledError:
            raise

    def start(self) -> None:
        if self._task is None:
            self._stop = False
            self._task = asyncio.create_task(self._flush_loop())

    async def stop(self) -> None:
        self._stop = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        await self._flush()
