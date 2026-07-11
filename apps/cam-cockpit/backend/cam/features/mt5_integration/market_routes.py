"""
Rotas de market data do Inspetor de Ativo — ADR-014 / SPEC-Inspetor.

READ-ONLY. Reaproveita o bridge ZeroMQ já existente (`MT5BridgeClient`) via o
service singleton de `routes.py`. Nenhum endpoint envia ordem (Art. 35º).

Endpoints:
- GET  /api/v1/mt5/symbols          — lista de símbolos do MT5 (EA GET_SYMBOLS)
- GET  /api/v1/mt5/symbol/{ticker}  — resolução + classificação de tipo
- GET  /api/v1/mt5/candles          — OHLCV histórico (EA GET_CANDLES) + persiste D1
- WS   /api/v1/mt5/ws/market/{symbol} — tick/book ao vivo + status

Falha segura: bridge offline → 503 com payload padronizado; WS emite
{"type":"status","state":"OFFLINE"} e não mente sobre dado fresco.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from cam._shared.infra import async_session_factory
from cam.features.mt5_integration.candle_store import upsert_daily_candles
from cam.features.mt5_integration.routes import _service
from cam.features.mt5_integration.schemas import (
    CandlesResponse,
    SymbolMeta,
    SymbolsResponse,
)
from cam.features.mt5_integration.symbol_resolver import resolve

router = APIRouter(prefix="/api/v1/mt5", tags=["mt5-market-data"])
_log = logging.getLogger("cam.inspetor")

_VALID_TF = {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"}


def _offline() -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": "MT5_BRIDGE_OFFLINE",
            "since": datetime.now(UTC).isoformat(),
            "message": "Bridge MT5 desconectada — abra o MT5 e atache o cam_bridge.",
        },
    )


@router.get("/symbols", response_model=SymbolsResponse)
async def list_symbols():
    if not _service.bridge.is_alive():
        return _offline()
    resp = await _service.get_symbols()
    if resp.get("status") != "ok":
        return JSONResponse(status_code=502, content=resp)
    return SymbolsResponse(symbols=resp.get("data", []))


@router.get("/symbol/{ticker}", response_model=SymbolMeta)
async def symbol_meta(ticker: str) -> SymbolMeta:
    r = resolve(ticker)
    return SymbolMeta(**r.to_dict())


@router.get("/candles", response_model=CandlesResponse)
async def candles(
    symbol: str = Query(..., min_length=1),
    timeframe: str = Query("H1"),
    count: int = Query(200, ge=1, le=5000),
):
    if timeframe not in _VALID_TF:
        return JSONResponse(
            status_code=422,
            content={"error": "INVALID_TIMEFRAME", "timeframe": timeframe},
        )
    if not _service.bridge.is_alive():
        return _offline()

    resp = await _service.get_candles(symbol, timeframe, count)
    if resp.get("status") != "ok":
        return JSONResponse(status_code=502, content=resp)

    data = resp["data"]
    candles_raw = data.get("candles", [])
    out = CandlesResponse(
        symbol=data["symbol"],
        timeframe=timeframe,  # type: ignore[arg-type]
        candles=[
            {
                "time": c["ts"],
                "open": c["o"],
                "high": c["h"],
                "low": c["l"],
                "close": c["c"],
                "volume": c["v"],
            }
            for c in candles_raw
        ],
    )

    # Persiste candles diários para o slice `regime` (lê cam_inspector_candles).
    # Best-effort: falha de banco não derruba a resposta de mercado.
    if timeframe == "D1" and candles_raw:
        try:
            async with async_session_factory() as session:
                await upsert_daily_candles(session, data["symbol"], candles_raw)
        except Exception:
            pass

    return out


@router.get("/probe-ticks")
async def probe_ticks(
    symbol: str = Query(..., min_length=1),
    count: int = Query(500, ge=1, le=5000),
):
    """
    Diagnóstico Research v0.5: o feed do MT5 entrega flag de agressor?

    Decide empiricamente se OFI/tick (Cubo Rápido) é viável no CaM, em vez de
    assumir no papel. `aggressor_available=true` → há ticks com TICK_FLAG_BUY/SELL.
    """
    if not _service.bridge.is_alive():
        return _offline()
    resp = await _service.probe_ticks(symbol, count)
    if resp.get("status") != "ok":
        return JSONResponse(status_code=502, content=resp)
    return resp["data"]


@router.websocket("/ws/market/{symbol}")
async def ws_market(websocket: WebSocket, symbol: str) -> None:
    """Stream ao vivo de tick/book + status. Read-only."""
    await websocket.accept()
    sym = symbol.upper()

    # pede ao EA para observar este símbolo (tick + book ao vivo via MarketBookAdd)
    if _service.bridge.is_alive():
        try:
            sub = await _service.subscribe_symbol(sym)
            _log.info("inspetor WS subscribe %s -> %s", sym, sub)
        except Exception as exc:  # noqa: BLE001
            _log.warning("inspetor WS subscribe %s FALHOU: %s", sym, exc)
    else:
        _log.info("inspetor WS %s: bridge OFFLINE", sym)

    queue = _service.hub.subscribe(sym)
    await websocket.send_json(
        {
            "type": "status",
            "state": "ONLINE" if _service.bridge.is_alive() else "OFFLINE",
        }
    )
    try:
        while True:
            try:
                frame = await asyncio.wait_for(queue.get(), timeout=2.0)
                await websocket.send_json(frame)
            except TimeoutError:
                # heartbeat de status — não mente sobre dado fresco (R-09)
                await websocket.send_json(
                    {
                        "type": "status",
                        "state": "ONLINE" if _service.bridge.is_alive() else "OFFLINE",
                    }
                )
    except WebSocketDisconnect:
        pass
    finally:
        _service.hub.unsubscribe(sym, queue)
