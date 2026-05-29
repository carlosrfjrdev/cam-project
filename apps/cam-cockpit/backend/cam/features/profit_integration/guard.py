"""
Guard de feature flag — bloqueia endpoints Profit quando desativados.

SPEC v0.2.1 R20.02 — quando PROFIT_INTEGRATION_ENABLED=false, qualquer chamada
aos endpoints /api/v1/profit/* (e /api/v1/journal/import-csv) retorna 410 Gone
com payload estruturado orientando para uso dos endpoints /api/v1/mt5/*.

Reativacao manual via .env (R20.07) — sem mudanca de codigo.
"""
from fastapi import HTTPException, Request, status

from cam._shared import config as _config_module
from cam._shared.audit.logger import log_disabled_endpoint_attempt

DISABLED_PAYLOAD = {
    "error": "PROFIT_INTEGRATION_DISABLED",
    "message": (
        "Integração Profit está desativada desde 2026-05-25 (SPEC v0.2). "
        "Use endpoints /api/v1/mt5/*."
    ),
    "reactivation_doc": "/project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md §2.1.8",
    "since": "2026-05-25",
}


class FeatureDisabledException(HTTPException):
    """
    Marker exception — handler customizado em cam/api/main.py preserva o
    detail no top-level do body (formato SPEC v0.2.1 R20.02).
    """

    def __init__(self, payload: dict) -> None:
        super().__init__(status_code=status.HTTP_410_GONE, detail=payload)
        self.payload = payload


async def check_profit_enabled(request: Request) -> None:
    """
    Dependência FastAPI — levanta HTTP 410 se PROFIT_INTEGRATION_ENABLED=false.
    Registra cada tentativa em audit log (R21.05).
    """
    if not _config_module.settings.profit_integration_enabled:
        log_disabled_endpoint_attempt(
            endpoint=str(request.url.path),
            method=request.method,
            client_ip=(request.client.host if request.client else "unknown"),
            reason="PROFIT_INTEGRATION_DISABLED",
        )
        raise FeatureDisabledException(DISABLED_PAYLOAD)
