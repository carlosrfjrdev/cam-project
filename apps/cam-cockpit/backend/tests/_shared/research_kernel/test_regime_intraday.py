"""Testes do classificador de regime intraday (Efficiency Ratio)."""
from __future__ import annotations

from cam._shared.research_kernel.regime_intraday import (
    INDEFINIDO,
    LATERAL,
    TENDENCIA_ALTA,
    TENDENCIA_BAIXA,
    classify,
    efficiency_ratio,
    label_trade,
)

T0 = 1_000_000.0


def test_er_tendencia_limpa_proximo_de_1():
    closes = [float(x) for x in range(0, 16)]  # sobe 1 por barra: caminho == líquido
    er = efficiency_ratio(closes, 15)
    assert er == 1.0


def test_er_vaivem_proximo_de_0():
    closes = [100.0, 110.0, 100.0, 110.0, 100.0]  # net 0 → ER 0
    er = efficiency_ratio(closes, 4)
    assert er == 0.0


def test_er_dados_insuficientes_none():
    assert efficiency_ratio([1.0, 2.0], 15) is None


def test_classify_tendencia_alta():
    closes = [float(x) for x in range(0, 16)]
    assert classify(closes, lookback=15, trend_threshold=0.45) == TENDENCIA_ALTA


def test_classify_tendencia_baixa():
    closes = [float(x) for x in range(15, -1, -1)]  # desce
    assert classify(closes, lookback=15, trend_threshold=0.45) == TENDENCIA_BAIXA


def test_classify_lateral():
    closes = [100.0, 102.0, 99.0, 101.0, 100.0, 101.0, 99.0, 100.0]
    assert classify(closes, lookback=7, trend_threshold=0.45) == LATERAL


def test_classify_indefinido_sem_dados():
    assert classify([1.0, 2.0], lookback=15) == INDEFINIDO


def test_label_trade_usa_so_closes_ate_entrada():
    # candles sobem até a entrada (tendência), depois caem (não deve influenciar)
    candles = [{"ts": T0 + i * 120, "c": float(i)} for i in range(20)]
    entry_ts = T0 + 15 * 120  # entrada no candle 15
    label = label_trade(candles, entry_ts, lookback=15, trend_threshold=0.45)
    assert label == TENDENCIA_ALTA
