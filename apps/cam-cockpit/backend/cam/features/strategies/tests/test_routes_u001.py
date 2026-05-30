"""
TDD First — TASK-U001 (BL-UI-0): strategies router HTTP.

Garante:
  - Registry exposto via GET (lista + por id).
  - Promoção sem evidência → EVIDENCE_REQUIRED (Arts. 28º/29º).
  - Router montado no app (OpenAPI).
  - **Nenhum endpoint de strategies submete ordem** (Kevin, Art. 35º).
"""
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestStrategiesRoutes:
    async def test_get_strategies_returns_200_with_list(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/strategies")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_strategy_by_id(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(f"/api/v1/strategies/{uuid4()}")
        # Inexistente → 404 com code; existente → 200. Nunca 500.
        assert resp.status_code in (200, 404)
        if resp.status_code == 404:
            assert resp.json()["detail"]["code"] == "STRATEGY_NOT_FOUND"

    async def test_promote_without_evidence_returns_error(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/strategies/{uuid4()}/promote",
                json={"target_status": "backtested"},
            )
        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "EVIDENCE_REQUIRED"

    async def test_strategies_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/strategies" in paths
        assert any(p.endswith("/promote") for p in paths)

    async def test_no_order_submission_endpoint(self):
        """Kevin — nenhuma rota de strategies envia ordem."""
        paths = app.openapi()["paths"]
        strat_paths = [p for p in paths if p.startswith("/api/v1/strategies")]
        forbidden = ("order", "submit", "send", "execute", "fill")
        for p in strat_paths:
            assert not any(tok in p.lower() for tok in forbidden), p
