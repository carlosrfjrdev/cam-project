"""TDD First — TASK-U002 (BL-UI-0): holdings router montado."""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestHoldingsRouterMounted:
    async def test_get_holdings_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/carteira-hard/holdings")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_holdings_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/carteira-hard/holdings" in paths

    async def test_holding_rejects_invalid_source(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/carteira-hard/holdings",
                json={
                    "ticker": "PETR4",
                    "quantity": "100",
                    "avg_price": "30.00",
                    "source": "HACKER",
                },
            )
        # Pydantic rejeita source inválido (422) — nunca aceita.
        assert resp.status_code == 422
