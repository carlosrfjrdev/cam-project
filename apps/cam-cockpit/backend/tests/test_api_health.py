"""
T-A05 — Teste do health check da API.
"""
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    from cam.api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
