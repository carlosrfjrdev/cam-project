"""Construção do prompt enviado à IA para análise dos trades."""
from __future__ import annotations

import json

from cam.features.trade_analyzer.metrics import TradeMetrics

SYSTEM_PREAMBLE = (
    "Você é um analista quantitativo de day trade (mini-índice WIN). "
    "Receba MÉTRICAS JÁ CALCULADAS (confiáveis, não recalcule) e produza um "
    "diagnóstico FRIO e acionável: 3-5 erros de PROCESSO mais caros, com a "
    "evidência numérica de cada um, e correções concretas. Foque em sizing/mão, "
    "stop diário, perdas seguidas (tilt), overtrade, horário de edge e direção "
    "contra o fluxo. Não é coach emocional. Responda em português, em markdown."
)


def build_prompt(metrics: TradeMetrics, tick_summary: dict | None) -> str:
    payload = {
        "resumo": {
            "trades": metrics.total_trades,
            "resultado_bruto": metrics.gross_result,
            "win_rate_pct": metrics.win_rate,
            "payoff": metrics.payoff,
            "profit_factor": metrics.profit_factor,
            "media_gain": metrics.avg_win,
            "media_loss": metrics.avg_loss,
            "melhor_trade": metrics.best_trade,
            "pior_trade": metrics.worst_trade,
            "max_perdas_seguidas": metrics.max_loss_streak,
            "trades_ultracurtos_le30s": metrics.ultrashort_count,
            "resultado_ultracurtos": metrics.ultrashort_result,
            "periodo": metrics.period,
        },
        "por_dia": metrics.by_day,
        "por_hora": metrics.by_hour,
        "por_lado": metrics.by_side,
        "por_mao_qtd": metrics.by_qty,
    }
    if tick_summary:
        payload["ticks"] = tick_summary

    return (
        f"{SYSTEM_PREAMBLE}\n\n"
        "MÉTRICAS (JSON):\n```json\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n```\n\n"
        "Entregue: (1) Veredito em 1 linha. (2) Tabela dos erros mais caros "
        "(erro | evidência | correção). (3) Onde está o edge desperdiçado "
        "(horário/mão/lado). (4) Plano de 3 regras objetivas para o próximo pregão."
    )
