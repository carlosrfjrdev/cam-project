"""
TDD First — TASK-U007 (BL-UI-0, SEC CRÍTICO): Order Gateway decisions.

Expõe `cam_risk_decisions` SOMENTE para leitura. Garante que não há nenhum
verbo de submissão de ordem sob `/api/v1/order-gateway` (Kevin, Art. 35º).
"""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestOrderGatewayDecisions:
    async def test_get_decisions_returns_list(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/order-gateway/decisions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_filter_by_env_and_decision(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/order-gateway/decisions",
                params={"env": "demo", "decision": "REJECTED"},
            )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_endpoint_is_read_only(self):
        """Kevin — sob /order-gateway só existe GET. Nenhum POST/PUT de ordem."""
        paths = app.openapi()["paths"]
        og_paths = {
            p: m for p, m in paths.items() if p.startswith("/api/v1/order-gateway")
        }
        assert og_paths, "router order-gateway não montado"
        for p, methods in og_paths.items():
            assert set(methods.keys()) <= {"get"}, (p, list(methods))

    async def test_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/order-gateway/decisions" in paths
