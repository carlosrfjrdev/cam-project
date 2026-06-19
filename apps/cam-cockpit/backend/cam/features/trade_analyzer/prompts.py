"""Construção do prompt enviado à IA para análise dos trades + candles M2."""
from __future__ import annotations

import json

from cam.features.trade_analyzer.metrics import TradeMetrics

SYSTEM_PREAMBLE = (
    "Você é um analista quantitativo de day trade (mini-índice WIN). Recebe: (1) "
    "MÉTRICAS já calculadas do operador e (2) ENRIQUECIMENTO por candle M2 — para "
    "cada operação, o que o preço fez DEPOIS da entrada (MFE/MAE em pontos) e se um "
    "setup fixo 1:3 (stop 100 / alvo 300 pts) teria batido ALVO, STOP ou nenhum. "
    "Tudo já vem calculado e confiável; NÃO recalcule. Produza um diagnóstico FRIO "
    "e acionável focado em: (a) oportunidades perdidas / 'mão de alface' (ganhou mas "
    "deixou muito na mesa — MFE alto vs capturado); (b) quantas entradas teriam "
    "atingido o 1:3 e quantas teriam stopado; (c) saídas precoces e cortes de "
    "perdedor tarde; (d) horário/lado/mão. Responda em português, em markdown."
)


def build_prompt(
    metrics: TradeMetrics,
    enrichment: dict,
    symbol: str,
    candle_status: str,
) -> str:
    payload = {
        "papel": symbol,
        "candles_m2": {
            "status": candle_status,  # db | fetched | partial | none
            "trades_avaliados": enrichment.get("trades_avaliados"),
        },
        "resumo": {
            "trades": metrics.total_trades,
            "resultado_bruto": metrics.gross_result,
            "win_rate_pct": metrics.win_rate,
            "payoff": metrics.payoff,
            "profit_factor": metrics.profit_factor,
            "media_gain": metrics.avg_win,
            "media_loss": metrics.avg_loss,
            "max_perdas_seguidas": metrics.max_loss_streak,
            "trades_ultracurtos_le30s": metrics.ultrashort_count,
            "periodo": metrics.period,
        },
        "por_dia": metrics.by_day,
        "por_hora": metrics.by_hour,
        "por_lado": metrics.by_side,
        "por_mao_qtd": metrics.by_qty,
        "setup_1x3": {
            "stop_pts": enrichment.get("stop_pts"),
            "alvo_pts": enrichment.get("target_pts"),
            "bateria_alvo": enrichment.get("rr13_alvo"),
            "bateria_stop": enrichment.get("rr13_stop"),
            "nenhum": enrichment.get("rr13_nenhum"),
            "taxa_alvo_pct": enrichment.get("rr13_taxa_alvo_pct"),
        },
        "oportunidade": {
            "mao_de_alface": enrichment.get("mao_de_alface"),
            "pts_deixados_na_mesa": enrichment.get("pts_deixados_na_mesa"),
            "mfe_medio": enrichment.get("mfe_medio"),
            "mae_medio": enrichment.get("mae_medio"),
        },
        "operacoes_detalhe": enrichment.get("trades", []),
    }
    if candle_status in ("partial", "none"):
        payload["candles_m2"]["aviso"] = (
            "Candles M2 ausentes/insuficientes no range — a análise por candle pode "
            "estar limitada (carregue o ativo no Operation Analyzer p/ persistir)."
        )

    return (
        f"{SYSTEM_PREAMBLE}\n\n"
        "DADOS (JSON):\n```json\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n```\n\n"
        "Entregue: (1) Veredito em 1 linha. (2) Tabela das oportunidades perdidas "
        "mais caras (operação | capturado | MFE | 1:3 teria batido? | correção). "
        "(3) Os erros de processo mais caros com evidência numérica. (4) Plano de 3 "
        "regras objetivas para o próximo pregão (sizing, stop, horário, deixar correr)."
    )
