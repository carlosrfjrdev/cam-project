"""
T-MT5-B01 — Guard de feature flag bloqueia endpoints Profit com 410 quando off.

SPEC v0.2.1 R20.02 — payload exato esperado:
{
  "error": "PROFIT_INTEGRATION_DISABLED",
  "message": "Integração Profit está desativada desde 2026-05-25 (SPEC v0.2). Use endpoints /api/v1/mt5/*.",
  "reactivation_doc": "/project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md §2.1.8",
  "since": "2026-05-25"
}
"""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestProfitDisabledGuard:
    """Com PROFIT_INTEGRATION_ENABLED=false (default), endpoints retornam 410."""

    async def test_validate_intention_returns_410(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/profit/validate-intention",
                json={"asset": "WIN", "direction": "LONG", "contracts": 1, "intended_stop_loss_points": "150"},
            )
        assert response.status_code == 410
        body = response.json()
        assert body["error"] == "PROFIT_INTEGRATION_DISABLED"
        assert "mt5" in body["message"].lower()
        assert body["since"] == "2026-05-25"

    async def test_import_csv_returns_410(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/journal/import-csv",
                files={"file": ("test.csv", b"empty", "text/csv")},
            )
        assert response.status_code == 410
        assert response.json()["error"] == "PROFIT_INTEGRATION_DISABLED"

    async def test_reconciliation_returns_410(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/profit/reconciliation/2026-05-25")
        assert response.status_code == 410
        assert response.json()["error"] == "PROFIT_INTEGRATION_DISABLED"


class TestProfitEnabledFunctional:
    """Quando flag reativada, endpoints voltam ao comportamento original (CA19.4)."""

    @pytest.mark.asyncio
    async def test_validate_intention_passes_through_when_enabled(self, monkeypatch):
        # Reativa flag programaticamente para validar reversibilidade
        from cam._shared import config as config_module
        monkeypatch.setattr(config_module.settings, "profit_integration_enabled", True)
        monkeypatch.setattr(config_module.settings, "mt5_integration_enabled", False)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/profit/validate-intention",
                json={"asset": "WIN", "direction": "LONG", "contracts": 1, "intended_stop_loss_points": "150"},
            )
        # Volta ao comportamento original (200 ou 400/422 — nao 410)
        assert response.status_code != 410
