"""
T-F03 — Testes de routes e integração DuckDB (stub) do Backtest Engine.
TDD First: estes testes foram escritos antes da implementação.
"""
import pytest


class TestBacktestRoutes:
    @pytest.mark.asyncio
    async def test_runs_endpoint_returns_list(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/api/v1/backtest/runs")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.asyncio
    async def test_research_query_read_only(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post(
                "/api/v1/backtest/research/query",
                json={"query": "SELECT 1 as test", "source_file": "test.csv"},
            )
        # Stub retorna 200 ou 422 — nunca 500
        assert r.status_code in (200, 422, 400)

    @pytest.mark.asyncio
    async def test_research_blocks_write_queries(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post(
                "/api/v1/backtest/research/query",
                json={
                    "query": "DROP TABLE cam_market_ticks",
                    "source_file": "test.csv",
                },
            )
        assert r.status_code in (400, 422, 403)
