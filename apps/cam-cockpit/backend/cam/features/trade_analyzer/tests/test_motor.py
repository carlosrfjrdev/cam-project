"""Teste de integração do motor estatístico (trades + candles → tabela por regime)."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from cam.features.trade_analyzer.metrics import Trade
from cam.features.trade_analyzer.motor import run_motor

BR = ZoneInfo("America/Sao_Paulo")


def _trade(hour: int, minute: int, entry: float) -> Trade:
    ab = datetime(2026, 6, 10, hour, minute, 0)
    fe = datetime(2026, 6, 10, hour, minute + 5, 0)
    return Trade(
        asset="WINQ26", abertura=ab, fechamento=fe, lado="C", qty=2,
        result=0.0, duration_s=300.0, entry_price=entry, exit_price=entry,
        direction="LONG",
    )


def _trend_candles(day_start_hour: int, entry_price: float) -> list[dict]:
    """
    Candles M2 do dia: 20 barras subindo (tendência) até a entrada, depois
    continua subindo forte (runner bate alvo grande).
    """
    base = datetime(2026, 6, 10, day_start_hour, 0, 0, tzinfo=BR).timestamp()
    candles = []
    px = entry_price - 200  # começa abaixo e sobe limpo até a entrada
    for i in range(40):
        px += 10
        candles.append({"ts": base + i * 120, "o": px, "h": px + 5, "l": px - 5, "c": px})
    return candles


def test_run_motor_tendencia_alta_bracket_positivo():
    # entrada às 10:30 (candle ~15 do dia que começou 10:00); preço de entrada
    # alinhado para haver janela forward subindo (runner).
    candles = _trend_candles(10, 170000.0)
    # entry no candle 15: preço lá ≈ (170000-200) + 16*10 = 169960
    entry_price = candles[15]["c"]
    trades = [_trade(10, 30, entry_price)]
    rep = run_motor(
        trades, candles, stops=[80], targets=[100], min_trades=1
    )
    assert rep["cobertura"]["com_candles"] == 1
    regimes = {s["segmento"]: s for s in rep["por_regime"]}
    assert "TENDENCIA_ALTA" in regimes
    best = regimes["TENDENCIA_ALTA"]["melhor"]
    assert best is not None
    assert best["expectancy_pts"] > 0  # tendência limpa → bracket positivo


def test_run_motor_reporta_cobertura_quando_sem_candles():
    trades = [_trade(10, 30, 170000.0)]
    rep = run_motor(trades, candles=[], stops=[80], targets=[100], min_trades=1)
    assert rep["cobertura"]["total_trades"] == 1
    assert rep["cobertura"]["sem_candles"] == 1
    assert rep["melhor_global"] is None


def test_run_motor_mae_vencedores_por_regime_presente():
    candles = _trend_candles(10, 170000.0)
    entry_price = candles[15]["c"]
    trades = [_trade(10, 30, entry_price)]
    rep = run_motor(trades, candles, stops=[80], targets=[100], min_trades=1)
    mae = rep["mae_vencedores_por_regime"]
    assert "TENDENCIA_ALTA" in mae
    assert mae["TENDENCIA_ALTA"]["n_vencedores"] == 1
