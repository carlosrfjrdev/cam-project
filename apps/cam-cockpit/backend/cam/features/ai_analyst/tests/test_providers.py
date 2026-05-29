"""
T-G02 — Testes TDD First: Providers Ollama e Anthropic.

Testa integração com LLMs locais (Ollama) e cloud (Anthropic),
fallback automático entre providers, e integração do ContentGuard
com o service para rejeição de análises proibidas.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestOllamaProvider:
    @pytest.mark.asyncio
    async def test_ollama_returns_string_response(self):
        from cam.features.ai_analyst.providers import OllamaProvider

        with patch("cam.features.ai_analyst.providers.httpx") as mock_httpx:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "response": "Análise do dia: 2 trades com aderência 100%."
            }
            mock_response.raise_for_status = MagicMock()
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_httpx.AsyncClient.return_value = mock_client

            provider = OllamaProvider(
                base_url="http://localhost:11434", model="llama3.1:8b"
            )
            result = await provider.analyze("Prompt de teste")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_ollama_failure_raises_exception(self):
        from cam.features.ai_analyst.providers import OllamaProvider

        with patch("cam.features.ai_analyst.providers.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=RuntimeError("Connection refused"))
            mock_httpx.AsyncClient.return_value = mock_client

            provider = OllamaProvider(base_url="http://localhost:11434")
            with pytest.raises(RuntimeError):
                await provider.analyze("Prompt")


class TestContentGuardIntegration:
    @pytest.mark.asyncio
    async def test_prohibited_analysis_is_rejected_and_logged(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FakeProvider:
            async def analyze(self, prompt: str) -> str:
                return "Recomendo comprar WIN agora — excelente oportunidade"

        guard = ContentGuard()
        svc = AIAnalystService(
            provider=FakeProvider(), guard=guard, notifier=None, collector=None
        )
        result = await svc._analyze_and_guard("prompt")
        assert result is None  # análise rejeitada

    @pytest.mark.asyncio
    async def test_valid_analysis_passes_guard(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FakeProvider:
            async def analyze(self, prompt: str) -> str:
                return (
                    "Você operou 2 vezes com aderência de 100%. "
                    "Padrão de loss concentrado nas primeiras horas."
                )

        guard = ContentGuard()
        svc = AIAnalystService(
            provider=FakeProvider(), guard=guard, notifier=None, collector=None
        )
        result = await svc._analyze_and_guard("prompt")
        assert result is not None
        assert "aderência" in result


class TestFallbackBehavior:
    @pytest.mark.asyncio
    async def test_anthropic_fallback_to_ollama_on_failure(self):
        from cam.features.ai_analyst.providers import ProviderWithFallback

        class FailingPrimary:
            async def analyze(self, prompt: str) -> str:
                raise Exception("API unavailable")

        class WorkingFallback:
            async def analyze(self, prompt: str) -> str:
                return "Análise via fallback"

        provider = ProviderWithFallback(
            primary=FailingPrimary(), fallback=WorkingFallback()
        )
        result = await provider.analyze("Prompt")
        assert result == "Análise via fallback"
