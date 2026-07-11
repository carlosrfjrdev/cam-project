"""
Store de preferências do app (JSON em disco). Simples e best-effort.

Arquivo: <cam_journal_dir>/../app_settings.json  (ex.: ~/.cam/app_settings.json)
"""
from __future__ import annotations

import json
from pathlib import Path

from cam._shared.config import settings

# Provedores de dados de mercado. "mt5" funcional; "profit" em casca (bridge
# ProfitDLL existe mas ainda não conectado — ver feature profit_bridge).
VALID_PROVIDERS = ("mt5", "profit")
DEFAULT_PROVIDER = "mt5"

# Provedores realmente operacionais hoje (o resto é casca/seleção sem efeito).
ACTIVE_PROVIDERS = ("mt5",)


def _path() -> Path:
    return Path(settings.cam_journal_dir).parent / "app_settings.json"


def _read() -> dict:
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write(data: dict) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_market_data_provider() -> str:
    prov = _read().get("market_data_provider", DEFAULT_PROVIDER)
    return prov if prov in VALID_PROVIDERS else DEFAULT_PROVIDER


def set_market_data_provider(provider: str) -> str:
    provider = (provider or "").lower().strip()
    if provider not in VALID_PROVIDERS:
        raise ValueError(f"provider inválido: {provider}. Use {VALID_PROVIDERS}.")
    data = _read()
    data["market_data_provider"] = provider
    _write(data)
    return provider


def is_active(provider: str) -> bool:
    return provider in ACTIVE_PROVIDERS
