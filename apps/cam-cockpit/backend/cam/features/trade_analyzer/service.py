"""
Orquestra a análise: parse report → métricas → candles M2 do range (busca/persiste
se faltar) → enriquecimento (1:3, MFE/MAE, mão de alface) → IA.

Provider e modelo selecionáveis (catálogo): anthropic/openai/deepseek/ollama.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from cam.features.trade_analyzer import prompts
from cam.features.trade_analyzer.candle_data import ensure_m2
from cam.features.trade_analyzer.catalog import (
    ProviderNotConfiguredError,
    build_client,
)
from cam.features.trade_analyzer.enrichment import enrich
from cam.features.trade_analyzer.metrics import Trade, compute_metrics, parse_report
from cam.features.trade_analyzer.motor import run_motor

BR_TZ = ZoneInfo("America/Sao_Paulo")

__all__ = ["analyze", "EmptyReportError", "ProviderNotConfiguredError"]


class EmptyReportError(ValueError):
    """Report não reconhecido / sem trades."""


def _symbol_of(trades: list[Trade]) -> str:
    return Counter(t.asset for t in trades).most_common(1)[0][0]


def _range(trades: list[Trade]) -> tuple[datetime, datetime]:
    start = min(t.abertura for t in trades).replace(
        hour=0, minute=0, second=0, tzinfo=BR_TZ
    )
    end = max(t.fechamento for t in trades).replace(
        hour=23, minute=59, second=59, tzinfo=BR_TZ
    )
    return start, end


async def analyze(
    report_bytes: bytes,
    provider: str,
    model: str | None = None,
    report_filename: str = "report.csv",
) -> dict:
    trades = parse_report(report_bytes)
    if not trades:
        raise EmptyReportError(
            "Nenhum trade reconhecido. Esperado layout 'Ativo;Abertura;Fechamento;...'."
        )
    metrics = compute_metrics(trades)
    metrics_dict = asdict(metrics)
    symbol = _symbol_of(trades)
    start, end = _range(trades)

    # candles M2 do range: usa research_bars; busca+persiste do MT5 se faltar
    candles, candle_status = await ensure_m2(symbol, start, end)
    enrichment = enrich(trades, candles)

    # Motor estatístico: varredura stop×alvo + expectância por regime/hora/lado
    # (responde "qual stop sobrevive ao ruído em cada regime?"). Reusa os mesmos
    # candles já buscados — degrada para cobertura vazia se faltarem.
    motor = run_motor(trades, candles)

    prompt = prompts.build_prompt(metrics, enrichment, symbol, candle_status)

    client, model_id = build_client(provider, model)
    narrative = await client.analyze(prompt)

    saved = {"id": None, "created_at": None}
    try:
        from cam.features.trade_analyzer import repository

        saved = await repository.save_analysis(
            provider=provider.lower(),
            model=model_id,
            symbol=symbol,
            report_filename=report_filename,
            report_content=report_bytes,
            metrics=metrics_dict,
            tick_summary=enrichment,  # guarda o enriquecimento junto
            tick_status=candle_status,
            narrative=narrative,
        )
    except Exception:  # noqa: BLE001
        pass

    return {
        "id": saved.get("id"),
        "created_at": saved.get("created_at"),
        "provider": provider.lower(),
        "model": model_id,
        "narrative": narrative,
        "metrics": metrics_dict,
        "symbol": symbol,
        "enrichment": enrichment,
        "motor": motor,
        "candle_status": candle_status,
        "candles_count": len(candles),
    }
