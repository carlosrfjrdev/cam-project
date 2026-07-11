"""TDD First — TASK-U003 (BL-UI-0): robot_orchestrator router (read-only)."""
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestRobotOrchestratorRoutes:
    async def test_get_robots_returns_list(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/robots")
        assert resp.status_code == 200
        body = resp.json()
        assert "robots" in body and isinstance(body["robots"], list)
        assert body["multi_strategy_enabled"] is False

    async def test_get_robot_adherence(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(f"/api/v1/robots/{uuid4()}/adherence")
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            body = resp.json()
            assert "individual_adherence" in body
            assert "aggregate_adherence" in body
            assert "limits" in body

    async def test_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/robots" in paths

    async def test_no_write_orchestration_endpoint(self):
        """Kevin — nenhuma rota de robots dispara orquestração/ordem."""
        paths = app.openapi()["paths"]
        robot_paths = {p: m for p, m in paths.items() if p.startswith("/api/v1/robots")}
        for p, methods in robot_paths.items():
            assert set(methods.keys()) <= {"get"}, (p, list(methods))
