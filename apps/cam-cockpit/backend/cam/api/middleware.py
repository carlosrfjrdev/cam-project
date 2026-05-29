"""
Middleware do CaM Cockpit API.

- CORS: permite apenas localhost (cockpit local, mono-operador)
- Structlog request logging: registra toda requisição com método, path e status
"""
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from cam._shared.audit import get_logger

logger = get_logger(__name__)


def add_middleware(app: FastAPI) -> None:
    """Registra todos os middlewares no app FastAPI."""
    _add_cors(app)
    _add_request_logging(app)


def _add_cors(app: FastAPI) -> None:
    """CORS restrito a localhost — cockpit não é exposto na rede."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternativo
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _add_request_logging(app: FastAPI) -> None:
    """Log estruturado de todas as requisições."""

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: object) -> Response:
            start = time.perf_counter()
            response: Response = await call_next(request)  # type: ignore[operator]
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            return response

    app.add_middleware(RequestLoggingMiddleware)


class WebSocketStub:
    """
    Stub para WebSocket de P&L live.
    Será implementado em T-E01 (Bloco E — Frontend).
    """

    pass
