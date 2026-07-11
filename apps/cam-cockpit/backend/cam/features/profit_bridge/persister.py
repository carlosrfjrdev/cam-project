"""
Persiste ticks do Profit em `cam_market_ticks` (corpus), em lote.

Mesmo padrão do `mt5_integration.tick_persister`: os callbacks da DLL (threads
próprias) só ENFILEIRAM num buffer thread-safe; um loop async drena e faz flush
periódico em lote. Best-effort — falha de banco não derruba o stream.
"""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

_log = logging.getLogger("cam.profit_bridge.persister")

_INSERT = text(
    """
    INSERT INTO cam_market_ticks (asset, price, volume, timestamp, source)
    VALUES (:asset, :price, :volume, to_timestamp(:ts_s), :source)
    """
)

_FLUSH_INTERVAL_S = 1.0
_MAX_BUFFER = 50_000


class ProfitTickPersister:
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        self._factory = session_factory
        self._buffer: deque[dict] = deque()
        self._task: asyncio.Task | None = None
        self._stop = False
        self.total_persisted = 0

    def on_tick(self, tick: dict) -> None:
        """Handler chamado pelos callbacks da DLL (thread da DLL). Só enfileira."""
        if len(self._buffer) < _MAX_BUFFER:
            self._buffer.append(
                {
                    "asset": tick["asset"][:10],
                    "price": tick["price"],
                    "volume": int(tick.get("quantity") or 0),
                    "ts_s": tick["ts_epoch"],
                    "source": tick.get("source", "profit.profitdll"),
                }
            )

    async def _flush(self) -> None:
        rows = []
        while self._buffer:
            rows.append(self._buffer.popleft())
        if not rows:
            return
        try:
            async with self._factory() as session:
                await session.execute(_INSERT, rows)
                await session.commit()
            self.total_persisted += len(rows)
        except Exception:  # noqa: BLE001 — corpus best-effort (não propaga)
            _log.exception("flush profit ticks falhou")

    async def _loop(self) -> None:
        while not self._stop:
            await asyncio.sleep(_FLUSH_INTERVAL_S)
            await self._flush()

    def start(self) -> None:
        if self._task is None:
            self._stop = False
            self._task = asyncio.create_task(self._loop())

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
