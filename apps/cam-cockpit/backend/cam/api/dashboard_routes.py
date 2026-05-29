"""
Rotas agregadas do dashboard — composer autorizado (ADR-013).

Endpoints aqui cruzam multiplas features (kill_switch, fiscal, journal, etc.)
e por isso vivem na camada `cam/api/` que e o unico compositor permitido.

Endpoints:
    GET /api/v1/risk/status      → estado consolidado do Risk Engine
    GET /api/v1/risk/decisions   → historico de decisoes (stub vazio sem DB)
    GET /api/v1/settings         → status real de servicos externos
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import APIRouter

from cam._shared.config import settings as cam_settings
from cam.features.kill_switch.routes import _service as kill_switch_service

router = APIRouter(tags=["dashboard"])


@router.get("/api/v1/risk/status")
async def risk_status() -> dict[str, Any]:
    """
    Estado consolidado do Risk Engine.

    Agrega: kill_switch, fase (POV inicial: FASE_1), conformidade fiscal stub,
    limites POV vigentes, P&L diario (stub sem DB).
    """
    ks = await kill_switch_service.get_status()
    return {
        "kill_switch_active": ks.active,
        "kill_switch_last_reason": ks.last_reason,
        "current_phase": 1,
        "tax_compliant": True,
        "daily_pnl_net": 0.0,
        "daily_loss_limit": 150.0,
        "weekly_loss_limit": 350.0,
        "monthly_loss_limit": 750.0,
        "gain_lock_reached": False,
        "open_positions": 0,
    }


@router.get("/api/v1/risk/decisions")
async def risk_decisions(limit: int = 50) -> list[dict[str, Any]]:
    """
    Historico de decisoes do Risk Engine.

    Stub: retorna lista vazia ate persistencia em cam_risk_decisions estar wired
    (TD-025). Schema preservado para a UI nao quebrar.
    """
    _ = limit
    return []


async def _ollama_alive() -> bool:
    url = cam_settings.ollama_base_url.rstrip("/") + "/api/tags"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(url)
        return r.status_code == 200
    except Exception:
        return False


@router.get("/api/v1/settings")
async def get_settings() -> dict[str, Any]:
    """Status real dos servicos. Nao expoe secrets (apenas booleanos)."""
    return {
        "telegram_configured": bool(cam_settings.telegram_bot_token and cam_settings.telegram_chat_id),
        "anthropic_configured": bool(cam_settings.anthropic_api_key),
        "ollama_configured": await _ollama_alive(),
        "database_connected": _database_connected(),
        "profit_csv_path": os.environ.get("CAM_PROFIT_CSV_PATH"),
        "database_url_host": _extract_db_host(cam_settings.database_url),
        "constitution_loaded": _constitution_loaded(),
        # T-TD-v0.2-06 (SPEC v0.3) — feature flags expostas
        "feature_flags": {
            "profit_integration_enabled": cam_settings.profit_integration_enabled,
            "mt5_integration_enabled": cam_settings.mt5_integration_enabled,
            "websocket_pnl_real_data": cam_settings.websocket_pnl_real_data,
        },
    }


def _database_connected() -> bool:
    """Tentativa rapida de conexao com o banco — falha silenciosa se offline."""
    try:
        import psycopg
        from urllib.parse import urlparse

        url = cam_settings.database_url.replace("+psycopg", "").replace("postgresql+psycopg", "postgresql")
        parsed = urlparse(url)
        dsn = f"host={parsed.hostname} port={parsed.port or 5432} dbname={parsed.path.lstrip('/')} user={parsed.username} password={parsed.password}"
        with psycopg.connect(dsn, connect_timeout=1) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


def _extract_db_host(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url.replace("+psycopg", "")).hostname or "unknown"
    except Exception:
        return "unknown"


def _constitution_loaded() -> bool:
    from cam.features.constitution.routes import _resolve_constitution_file
    return _resolve_constitution_file() is not None
