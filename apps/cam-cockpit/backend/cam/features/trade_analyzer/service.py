"""
Orquestra a análise: parse report → métricas → resumo de ticks → IA.

Provider selecionável (anthropic | openai). Sem default fixo: a UI manda.
"""
from __future__ import annotations

import csv
import io
from collections import Counter
from dataclasses import asdict

from cam._shared.config import settings
from cam.features.ai_analyst.providers import AnthropicProvider, OpenAIProvider
from cam.features.trade_analyzer import prompts
from cam.features.trade_analyzer.metrics import compute_metrics, parse_report


class ProviderNotConfiguredError(RuntimeError):
    """Provider escolhido sem API key no .env."""


class EmptyReportError(ValueError):
    """Report não reconhecido / sem trades."""


def summarize_ticks(content: bytes | None) -> dict | None:
    """Resumo leve do CSV de ticks (extraído via bridge). Best-effort."""
    if not content:
        return None
    text = content.decode("utf-8", errors="replace")
    try:
        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        rows = list(reader)
    except csv.Error:
        return None
    if not rows:
        return None
    aggressor = Counter(
        (r.get("aggressor") or "").strip() for r in rows if r.get("aggressor")
    )
    by_date = Counter(r.get("date") for r in rows if r.get("date"))
    return {
        "total_ticks": len(rows),
        "por_data": dict(by_date),
        "agressor": {
            "compra_B": aggressor.get("B", 0),
            "venda_S": aggressor.get("S", 0),
        },
    }


def _build_provider(provider: str):
    p = provider.lower().strip()
    if p == "anthropic":
        if not settings.anthropic_api_key:
            raise ProviderNotConfiguredError(
                "ANTHROPIC_API_KEY ausente no .env — configure para usar Claude."
            )
        return AnthropicProvider(settings.anthropic_api_key), settings.anthropic_model
    if p == "openai":
        if not settings.openai_api_key:
            raise ProviderNotConfiguredError(
                "OPENAI_API_KEY ausente no .env — configure para usar OpenAI."
            )
        return OpenAIProvider(settings.openai_api_key), settings.openai_model
    raise ProviderNotConfiguredError(f"Provider desconhecido: {provider}")


async def analyze(
    report_bytes: bytes, ticks_bytes: bytes | None, provider: str
) -> dict:
    trades = parse_report(report_bytes)
    if not trades:
        raise EmptyReportError(
            "Nenhum trade reconhecido. Esperado layout 'Ativo;Abertura;Fechamento;...'."
        )
    metrics = compute_metrics(trades)
    tick_summary = summarize_ticks(ticks_bytes)
    prompt = prompts.build_prompt(metrics, tick_summary)

    client, model = _build_provider(provider)
    narrative = await client.analyze(prompt)

    return {
        "provider": provider.lower(),
        "model": model,
        "narrative": narrative,
        "metrics": asdict(metrics),
        "tick_summary": tick_summary,
    }
