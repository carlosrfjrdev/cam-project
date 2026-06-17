"""
Orquestra a análise: parse report → métricas → ticks do dia (AUTO do MT5) → IA.

Os ticks NÃO são mais enviados por upload: são puxados automaticamente da bridge
MT5 (GET_TICKS) para o símbolo e o período do report. Provider selecionável
(anthropic | openai). Sem default fixo: a UI manda.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cam._shared.config import settings
from cam.features.ai_analyst.providers import AnthropicProvider, OpenAIProvider
from cam.features.trade_analyzer import prompts
from cam.features.trade_analyzer.metrics import Trade, compute_metrics, parse_report

BR_TZ = ZoneInfo("America/Sao_Paulo")
FLAG_BUY = 4
FLAG_SELL = 8


class ProviderNotConfiguredError(RuntimeError):
    """Provider escolhido sem API key no .env."""


class EmptyReportError(ValueError):
    """Report não reconhecido / sem trades."""


def _symbol_of(trades: list[Trade]) -> str:
    return Counter(t.asset for t in trades).most_common(1)[0][0]


def _msc_range(trades: list[Trade]) -> tuple[int, int]:
    first = min(t.abertura for t in trades).replace(
        hour=0, minute=0, second=0, tzinfo=BR_TZ
    ) - timedelta(hours=3)  # buffer p/ tz do servidor de trade
    last = max(t.fechamento for t in trades).replace(
        hour=23, minute=59, second=59, tzinfo=BR_TZ
    )
    return int(first.timestamp() * 1000), int(last.timestamp() * 1000)


def summarize_tick_dicts(ticks: list[dict]) -> dict | None:
    """Resumo leve dos ticks vindos do MT5 (count, por data, agressor)."""
    if not ticks:
        return None
    by_date: Counter = Counter()
    aggr = {"B": 0, "S": 0}
    last_t = 0
    for t in ticks:
        ms = t.get("t", 0)
        last_t = max(last_t, ms)
        if ms:
            d = datetime.fromtimestamp(ms / 1000.0, tz=BR_TZ).strftime("%Y-%m-%d")
            by_date[d] += 1
        f = int(t.get("f") or 0)
        if f & FLAG_BUY:
            aggr["B"] += 1
        elif f & FLAG_SELL:
            aggr["S"] += 1
    last_iso = (
        datetime.fromtimestamp(last_t / 1000.0, tz=BR_TZ).isoformat()
        if last_t
        else None
    )
    return {
        "total_ticks": len(ticks),
        "por_data": dict(by_date),
        "agressor": {"compra_B": aggr["B"], "venda_S": aggr["S"]},
        "ultimo_tick": last_iso,
        "fonte": "mt5_auto",
    }


async def _fetch_ticks_from_mt5(
    symbol: str, trades: list[Trade]
) -> tuple[list[dict], str]:
    """Puxa os ticks do período direto da bridge MT5. Falha segura → ([], motivo)."""
    try:
        from cam.features.mt5_integration.routes import _service as mt5
    except Exception:  # noqa: BLE001
        return [], "integração MT5 indisponível"
    if not mt5.bridge.is_alive():
        return [], "bridge MT5 offline — atache o EA cam_bridge no gráfico"
    from_msc, to_msc = _msc_range(trades)
    try:
        ticks = await mt5.get_ticks_range(symbol, from_msc, to_msc)
    except Exception as exc:  # noqa: BLE001
        return [], f"falha ao buscar ticks: {exc}"
    return ticks, "ok"


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


async def analyze(report_bytes: bytes, provider: str) -> dict:
    trades = parse_report(report_bytes)
    if not trades:
        raise EmptyReportError(
            "Nenhum trade reconhecido. Esperado layout 'Ativo;Abertura;Fechamento;...'."
        )
    metrics = compute_metrics(trades)
    symbol = _symbol_of(trades)

    ticks, tick_status = await _fetch_ticks_from_mt5(symbol, trades)
    tick_summary = summarize_tick_dicts(ticks)
    prompt = prompts.build_prompt(metrics, tick_summary)

    client, model = _build_provider(provider)
    narrative = await client.analyze(prompt)

    return {
        "provider": provider.lower(),
        "model": model,
        "narrative": narrative,
        "metrics": asdict(metrics),
        "tick_summary": tick_summary,
        "tick_status": tick_status,
        "symbol": symbol,
    }
