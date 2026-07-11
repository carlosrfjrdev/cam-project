"""TDD First — TASK-U005 (BL-UI-0): research / AI workbench router."""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestResearchRoutes:
    async def test_get_correlation(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/research/correlation",
                params={"asset_a": "WIN", "asset_b": "WDO"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["asset_a"] == "WIN"
        assert "correlation" in body  # None em Fase 0 (sem séries)

    async def test_post_pair_trade_backtest(self):
        series = [
            {"timestamp": "2026-01-01T10:00:00Z", "price": "100.0"},
            {"timestamp": "2026-01-02T10:00:00Z", "price": "101.0"},
            {"timestamp": "2026-01-03T10:00:00Z", "price": "99.0"},
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/research/pair-trade-backtest",
                json={
                    "asset_a": "PETR4",
                    "asset_b": "PETR3",
                    "series_a": series,
                    "series_b": series,
                },
            )
        assert resp.status_code == 200
        assert "total_pnl" in resp.json()

    async def test_post_workbench_returns_json(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/research/workbench",
                json={"provider": "ollama", "prompt": "analise X"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "ollama"
        assert "prompt_hash" in body

    async def test_workbench_openai_blocked(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/research/workbench",
                json={"provider": "openai", "prompt": "analise X"},
            )
        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "OpenAINotEnabled"

    async def test_router_mounted(self):
        paths = app.openapi()["paths"]
        assert "/api/v1/research/correlation" in paths
