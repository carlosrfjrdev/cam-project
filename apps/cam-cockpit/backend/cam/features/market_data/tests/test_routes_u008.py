"""TDD First — TASK-U008 (BL-UI-0): market-data provenance + instruments + EA."""
import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestMarketDataProvenanceInstruments:
    async def test_get_provenance(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/market-data/provenance")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_get_instruments(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/market-data/instruments")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestEaControl:
    async def test_ea_status_and_version(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            st = await client.get("/api/v1/mt5/ea/status")
            ver = await client.get("/api/v1/mt5/ea/cam_risk_mirror_win/version")
        assert st.status_code == 200
        assert "eas" in st.json()
        assert ver.status_code == 200
        body = ver.json()
        assert "version" in body and "hash" in body and "paused" in body

    async def test_ea_pause_resume(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            paused = await client.post("/api/v1/mt5/ea/cam_risk_mirror_wdo/pause")
            resumed = await client.post("/api/v1/mt5/ea/cam_risk_mirror_wdo/resume")
        assert paused.status_code == 200 and paused.json()["paused"] is True
        assert resumed.status_code == 200 and resumed.json()["paused"] is False

    async def test_no_submit_order_via_ea_endpoint(self):
        """Kevin — nenhuma rota de EA submete ordem; só pause/resume/version."""
        paths = app.openapi()["paths"]
        ea_paths = [p for p in paths if p.startswith("/api/v1/mt5/ea")]
        assert ea_paths
        for p in ea_paths:
            assert not any(
                tok in p.lower() for tok in ("order", "submit", "send")
            ), p
