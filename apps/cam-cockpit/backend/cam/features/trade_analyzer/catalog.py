"""
Catálogo de providers/modelos de IA do Trade Analyzer + builder do client.

Providers: anthropic (Opus/Sonnet/Haiku), openai (GPT), deepseek (chat/reasoner)
e ollama (local, catálogo do .env). A UI lista provider → modelos; o analyze
recebe (provider, model).
"""
from __future__ import annotations

from cam._shared.config import settings
from cam.features.ai_analyst.providers import (
    AnthropicProvider,
    DeepSeekProvider,
    OllamaProvider,
    OpenAIProvider,
)


class ProviderNotConfiguredError(RuntimeError):
    """Provider sem API key / indisponível."""


# modelos por provider (id, label). ollama vem das settings (configurável).
def _catalog() -> dict[str, dict]:
    return {
        "anthropic": {
            "label": "Claude (Anthropic)",
            "configured": bool(settings.anthropic_api_key),
            "models": [
                {"id": "claude-opus-4-8", "label": "Opus 4.8"},
                {"id": "claude-sonnet-4-6", "label": "Sonnet 4.6"},
                {"id": "claude-haiku-4-5-20251001", "label": "Haiku 4.5"},
            ],
            "default": "claude-haiku-4-5-20251001",
        },
        "openai": {
            "label": "OpenAI (GPT)",
            "configured": bool(settings.openai_api_key),
            "models": [
                {"id": "gpt-4o", "label": "GPT-4o"},
                {"id": "gpt-4.1", "label": "GPT-4.1"},
                {"id": "gpt-4o-mini", "label": "GPT-4o mini"},
            ],
            "default": "gpt-4o",
        },
        "deepseek": {
            "label": "DeepSeek",
            "configured": bool(settings.deepseek_api_key),
            "models": [
                {"id": "deepseek-chat", "label": "DeepSeek Chat (V3)"},
                {"id": "deepseek-reasoner", "label": "DeepSeek Reasoner (R1)"},
            ],
            "default": "deepseek-chat",
        },
        "ollama": {
            "label": "Ollama (local)",
            "configured": True,  # local, sem key — erro em runtime se o server off
            "models": [{"id": m, "label": m} for m in settings.ollama_models],
            "default": settings.ollama_model,
        },
    }


def list_providers() -> list[dict]:
    out = []
    for pid, info in _catalog().items():
        out.append({
            "id": pid,
            "label": info["label"],
            "configured": info["configured"],
            "models": info["models"],
            "default_model": info["default"],
        })
    return out


def build_client(provider: str, model: str | None):
    """Retorna (client, model_id) do provider escolhido. Valida key/modelo."""
    p = (provider or "").lower().strip()
    cat = _catalog().get(p)
    if cat is None:
        raise ProviderNotConfiguredError(f"provider desconhecido: {provider}")
    model_id = model or cat["default"]

    if p == "anthropic":
        if not settings.anthropic_api_key:
            raise ProviderNotConfiguredError("ANTHROPIC_API_KEY ausente no .env.")
        return AnthropicProvider(settings.anthropic_api_key, model=model_id), model_id
    if p == "openai":
        if not settings.openai_api_key:
            raise ProviderNotConfiguredError("OPENAI_API_KEY ausente no .env.")
        return OpenAIProvider(settings.openai_api_key, model=model_id), model_id
    if p == "deepseek":
        if not settings.deepseek_api_key:
            raise ProviderNotConfiguredError("DEEPSEEK_API_KEY ausente no .env.")
        return DeepSeekProvider(settings.deepseek_api_key, model=model_id), model_id
    if p == "ollama":
        return OllamaProvider(settings.ollama_base_url, model=model_id), model_id
    raise ProviderNotConfiguredError(f"provider não suportado: {provider}")
