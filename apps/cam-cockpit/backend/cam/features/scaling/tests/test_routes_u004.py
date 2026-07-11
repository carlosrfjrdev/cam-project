"""TDD First — TASK-U004 (BL-UI-0): scaling router."""
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestScalingRoutes:
    async def test_get_scaling_events(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/scaling/events")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_eligibility(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(f"/api/v1/scaling/eligibility/{uuid4()}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["scaling_enabled"] is False
        assert "criteria" in body

    async def test_get_blocked_attempts_histogram(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/scaling/blocked-attempts")
        assert resp.status_code == 200
        body = resp.json()
        assert "histogram" in body
        # 5 critérios canônicos Art. 11-B presentes.
        for c in ("PF", "WR", "EXP", "DD", "ADH"):
            assert c in body["histogram"]

    async def test_post_revoke(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/scaling/revoke/{uuid4()}",
                json={"reason": "teste", "cooldown_days": 7},
            )
        assert resp.status_code == 201
        assert resp.json()["cooldown_days"] == 7

    async def test_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/scaling/events" in paths
