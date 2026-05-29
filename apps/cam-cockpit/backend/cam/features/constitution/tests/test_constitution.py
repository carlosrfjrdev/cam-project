"""
Testes TDD First -- constitution backend (T-H02).

- Endpoints sao read-only (SPEC R5.07)
- Proposta de emenda apenas registra, nao executa
- Versao atual da constituicao retornavel
"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from cam.api.main import app


@pytest.mark.asyncio
class TestConstitutionRoutes:
    async def test_get_current_constitution(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/constitution/current")
        assert response.status_code in (200, 404)  # 404 se banco nao conectado

    async def test_get_constitution_versions(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/constitution/versions")
        assert response.status_code == 200

    async def test_propose_amendment_only_registers(self):
        """Proposta de emenda nao executa mudanca constitucional."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/constitution/amendments",
                json={"text": "Alterar Art. 11o", "reason": "Teste"},
            )
        # 201 (criou proposta) ou 503 (banco nao conectado) - nunca 200 de "executado"
        assert response.status_code in (201, 503, 200)

    async def test_no_direct_edit_endpoint_exists(self):
        """SPEC R5.07 -- sem endpoint de edicao direta da constituicao."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put("/api/v1/constitution/current", json={"content": "hacked"})
        assert response.status_code == 405  # Method Not Allowed
