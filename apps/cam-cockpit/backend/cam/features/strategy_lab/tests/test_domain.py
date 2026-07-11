"""Testes do domínio do StrategyLab (R-11/R-19) — puros, valores brutos."""
from datetime import datetime

from cam.features.strategy_lab.domain import (
    Leg,
    LegTrade,
    Unit,
    aggregate_by_pair,
)


def _leg(pair_id, leg, sym, p_in, p_out, qty=1, pv=1.0):
    return LegTrade(
        pair_id=pair_id,
        leg=leg,
        symbol=sym,
        ts_entry=datetime(2026, 6, 3, 9, 0),
        price_entry=p_in,
        ts_exit=datetime(2026, 6, 3, 10, 0),
        price_exit=p_out,
        qty=qty,
        exit_reason="target",
        point_value=pv,
    )


def test_pnl_long_bruto() -> None:
    # compra 100, vende 110, 1 contrato, ponto vale 1 → +10
    leg = _leg(1, Leg.LONG, "WIN", 100, 110)
    assert leg.pnl_bruto == 10.0


def test_pnl_short_bruto() -> None:
    # vende 110, recompra 100 → +10 (short ganha na queda)
    leg = _leg(1, Leg.SHORT, "WIN", 110, 100)
    assert leg.pnl_bruto == 10.0


def test_point_value_aplicado() -> None:
    # WIN: 5 pontos, ponto vale 0.20 → 5 × 0.20 = 1.0
    leg = _leg(1, Leg.LONG, "WIN", 100000, 100005, qty=1, pv=0.20)
    assert abs(leg.pnl_bruto - 1.0) < 1e-9


def test_single_e_par_de_uma_perna() -> None:
    legs = [_leg(1, Leg.LONG, "WIN", 100, 110)]
    pairs = aggregate_by_pair(legs)
    assert len(pairs) == 1
    assert pairs[0].pnl_bruto == 10.0
    assert pairs[0].is_win is True


def test_par_duas_pernas_agrega() -> None:
    # par: long WIN +10, short WDO +5 → spread +15
    legs = [
        _leg(7, Leg.LONG, "WIN", 100, 110),
        _leg(7, Leg.SHORT, "WDO", 200, 195),
    ]
    pairs = aggregate_by_pair(legs)
    assert len(pairs) == 1
    assert pairs[0].pnl_bruto == 15.0
    assert len(pairs[0].legs) == 2


def test_multiplos_trades_separados_por_pair_id() -> None:
    legs = [
        _leg(1, Leg.LONG, "WIN", 100, 110),
        _leg(2, Leg.LONG, "WIN", 110, 105),  # perde 5
    ]
    pairs = aggregate_by_pair(legs)
    assert len(pairs) == 2
    assert pairs[0].is_win is True
    assert pairs[1].is_win is False


def test_volume_financeiro() -> None:
    leg = _leg(1, Leg.LONG, "WIN", 100, 110, qty=2, pv=1.0)
    # (100 + 110) × 2 = 420
    assert leg.volume_financeiro == 420.0


def test_unit_enum() -> None:
    assert Unit.SINGLE.value == "single"
    assert Unit.PAIR.value == "pair"
