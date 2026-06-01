"""
MarketHub — fan-out de tick/book ao vivo para clientes WebSocket do Inspetor.

ADR-014 / SPEC-Inspetor R-05, R-09. Read-only: apenas distribui o que o EA
publica em `mt5.tick` e `mt5.book`. Falha segura: sem heartbeat → status OFFLINE
é decidido pelo bridge; o hub só repassa frames.

Padrão: cada cliente WS registra uma asyncio.Queue para um símbolo; os handlers
do bridge empurram o frame (já parseado) nas filas do símbolo correspondente.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any


class MarketHub:
    """Distribui ticks/books por símbolo para filas de assinantes WS."""

    def __init__(self) -> None:
        # symbol(upper) -> set de filas
        self._subscribers: dict[str, set[asyncio.Queue[dict[str, Any]]]] = {}
        # último frame conhecido por símbolo (para enviar snapshot ao conectar)
        self._last_tick: dict[str, dict[str, Any]] = {}
        self._last_book: dict[str, dict[str, Any]] = {}

    # ---------------- assinatura WS ----------------

    def subscribe(self, symbol: str) -> asyncio.Queue[dict[str, Any]]:
        sym = symbol.upper()
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=200)
        self._subscribers.setdefault(sym, set()).add(q)
        # entrega imediata do último estado conhecido, se houver
        if sym in self._last_tick:
            q.put_nowait({"type": "tick", **self._last_tick[sym]})
        if sym in self._last_book:
            q.put_nowait({"type": "book", **self._last_book[sym]})
        return q

    def unsubscribe(self, symbol: str, q: asyncio.Queue[dict[str, Any]]) -> None:
        sym = symbol.upper()
        subs = self._subscribers.get(sym)
        if subs and q in subs:
            subs.discard(q)
            if not subs:
                self._subscribers.pop(sym, None)

    # ---------------- handlers do bridge ----------------

    async def on_tick(self, payload: bytes) -> None:
        self._dispatch(payload, "tick", self._last_tick)

    async def on_book(self, payload: bytes) -> None:
        self._dispatch(payload, "book", self._last_book)

    def _dispatch(
        self, payload: bytes, kind: str, cache: dict[str, dict[str, Any]]
    ) -> None:
        try:
            data = json.loads(payload.decode("utf-8", errors="replace"))
        except (ValueError, AttributeError):
            return
        symbol = str(data.get("symbol", "")).upper()
        if not symbol:
            return
        cache[symbol] = data
        frame = {"type": kind, **data}
        for q in list(self._subscribers.get(symbol, set())):
            try:
                q.put_nowait(frame)
            except asyncio.QueueFull:
                # cliente lento — descarta frame mais antigo e tenta de novo
                try:
                    q.get_nowait()
                    q.put_nowait(frame)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass
