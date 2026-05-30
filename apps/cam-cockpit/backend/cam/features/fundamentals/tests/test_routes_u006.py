"""TDD First — TASK-U006 (BL-UI-0): fundamentals / dividends / policy router."""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestFundamentalsRoutes:
    async def test_get_fundamentals_ticker(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/fundamentals/PETR4")
        assert resp.status_code == 200
        body = resp.json()
        # 7 indicadores R-20.
        for k in ("dy", "pl", "pvp", "roe", "div_liq_ebitda", "payout", "roic"):
            assert k in body

    async def test_get_fundamentals_unknown_is_404(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/fundamentals/ZZZZ9")
        assert resp.status_code == 404

    async def test_get_dividends_calendar(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/dividends/calendar")
        assert resp.status_code == 200
        assert "events" in resp.json()

    async def test_get_policy_alerts_never_blocking(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/carteira-hard/policy-alerts")
        assert resp.status_code == 200
        body = resp.json()
        assert "alerts" in body
        # R-13: alertas nunca bloqueiam.
        assert body["blocking"] is False

    async def test_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/fundamentals/{ticker}" in paths
        assert "/api/v1/dividends/calendar" in paths
