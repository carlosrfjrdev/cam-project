"""
Rotas das preferências do app.

GET /api/v1/app-settings/market-data-provider  → provider atual + opções
PUT /api/v1/app-settings/market-data-provider  → {"provider": "mt5"|"profit"}
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from cam.features.app_settings import store

router = APIRouter(prefix="/api/v1/app-settings", tags=["app-settings"])


class ProviderUpdate(BaseModel):
    provider: str


@router.get("/market-data-provider")
async def get_provider() -> dict:
    current = store.get_market_data_provider()
    return {
        "provider": current,
        "active": store.is_active(current),
        "options": [
            {"id": "mt5", "label": "MetaTrader 5", "status": "active"},
            {"id": "profit", "label": "Profit (ProfitDLL)", "status": "casca"},
        ],
    }


@router.put("/market-data-provider")
async def set_provider(body: ProviderUpdate):
    try:
        current = store.set_market_data_provider(body.provider)
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"error": str(exc)})
    return {
        "provider": current,
        "active": store.is_active(current),
        "note": (
            "Profit ainda em casca — a coleta segue desativada até o profit_bridge "
            "ser conectado (chave de ativação)."
            if not store.is_active(current)
            else "MT5 ativo como provedor de dados."
        ),
    }
