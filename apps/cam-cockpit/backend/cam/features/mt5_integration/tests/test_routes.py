"""
T-MT5-D01 + T-MT5-D02 — Routes HTTP + tratamento OFFLINE.
"""
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestMT5Routes:
    async def test_bridge_status_returns_offline_when_no_heartbeat(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/mt5/bridge/status")
        assert response.status_code == 200
        body = response.json()
        assert body["state"] == "OFFLINE"
        assert body["host"] == "127.0.0.1"

    async def test_positions_returns_503_when_offline(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/mt5/positions")
        assert response.status_code == 503
        body = response.json()
        assert body["error"] == "MT5_BRIDGE_OFFLINE"

    async def test_validate_intention_works_even_offline(self):
        """Validacao do Risk Engine NAO depende da bridge — Art. 15o."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/mt5/validate-intention",
                json={"asset": "WIN", "direction": "LONG", "contracts": 3, "intended_stop_loss_points": "150"},
            )
        # 422 porque contracts=3 falha no schema (Art. 11o)
        assert response.status_code == 422

    async def test_validate_intention_returns_decision(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/mt5/validate-intention",
                json={"asset": "WIN", "direction": "LONG", "contracts": 1, "intended_stop_loss_points": "150"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "approved" in body
        assert isinstance(body["approved"], bool)

    async def test_restart_requires_confirm(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/mt5/bridge/restart", json={"confirm": False})
        assert response.status_code == 400

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/mt5/bridge/restart", json={"confirm": True})
        assert response.status_code == 200
        assert response.json()["status"] in ("restarting", "restarted")
