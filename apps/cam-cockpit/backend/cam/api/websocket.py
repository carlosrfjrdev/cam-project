"""
WebSocket broker para P&L live e alertas em tempo real.

T-TD-026 (SPEC v0.3) — stub funcional emitindo P&L a cada 5 segundos.
Quando WEBSOCKET_PNL_REAL_DATA=true em .env, busca de fonte real (a implementar
quando journal repository estiver wired ao DB).

Referencia DAS §5 (contratos externos Frontend <-> Backend).
"""
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from cam._shared.config import settings

router = APIRouter()

HEARTBEAT_INTERVAL_SEC = 5


@router.websocket("/api/v1/ws/pnl")
async def pnl_websocket(ws: WebSocket) -> None:
    """
    Emite snapshot de P&L a cada 5s.

    Stub em v0.3: emite zeros se WEBSOCKET_PNL_REAL_DATA=false.
    Quando true, consulta banco (a implementar — fica como TD ate ter
    journal repository wired). Frontend trata graciosamente.
    """
    await ws.accept()
    try:
        while True:
            payload = await _build_pnl_snapshot()
            await ws.send_json(payload)
            await asyncio.sleep(HEARTBEAT_INTERVAL_SEC)
    except WebSocketDisconnect:
        return
    except Exception:
        # nao propagar — encerra conexao limpa
        return


async def _build_pnl_snapshot() -> dict:
    """Stub: zeros quando real_data=false; placeholder para fonte real."""
    if settings.websocket_pnl_real_data:
        # TODO: consultar journal repository quando wired (TD-008/TD-022 family)
        pass

    return {
        "daily_pnl_gross": 0.0,
        "daily_pnl_net": 0.0,
        "open_positions": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "stub",
    }
