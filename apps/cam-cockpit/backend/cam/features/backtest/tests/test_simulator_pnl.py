"""
TDD First — BacktestSimulator P&L real (TASK-008 BL-A).
"""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Phase,
)
from cam._shared.risk import OrderCandidate
from cam.features.backtest.domain import BacktestConfig
from cam.features.backtest.simulator import BacktestSimulator


def _cfg(*, point_value="0.20", tp_points=None) -> BacktestConfig:
    return BacktestConfig(
        strategy_name="test",
        date_from=datetime(2026, 5, 27, tzinfo=UTC),
        date_to=datetime(2026, 5, 27, 18, tzinfo=UTC),
        phase=Phase.FASE_1,
        brokerage_per_contract=Decimal("2.50"),
        point_value=Decimal(str(point_value)),
        take_profit_points=Decimal(str(tp_points)) if tp_points else None,
    )


def _tick(ts, price):
    return {"timestamp": ts, "price": Decimal(str(price))}


def _make_strategy(at_index: int):
    """Cria função strategy que retorna OrderCandidate no tick at_index."""
    calls = {"n": 0}

    def fn(_tick):
        i = calls["n"]
        calls["n"] += 1
        if i == at_index:
            return OrderCandidate(
                asset=AssetType.WIN,
                direction=Direction.LONG,
                contracts=ContractCount(1),
                intended_stop_loss_points=Decimal("150"),
                is_setup_a_plus=True,
            )
        return None
    return fn


class TestSimulatorBasic:
    def test_zero_trades_when_strategy_returns_none(self):
        sim = BacktestSimulator()
        ticks = [_tick(datetime(2026, 5, 27, 11, m, tzinfo=UTC), 130000)
                 for m in range(5)]
        run = sim.run(_cfg(), ticks, lambda t: None)
        assert run.status == "COMPLETED"
        assert run.trades == []


class TestStopLossTrigger:
    def test_long_trade_hits_stop_loss(self):
        sim = BacktestSimulator()
        ts0 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        # Entry @ 130000, SL = 150 pontos → fecha quando preço ≤ 129850
        ticks = [
            _tick(ts0, 130000),     # entry tick (index 0)
            _tick(ts0, 130020),
            _tick(ts0, 129870),
            _tick(ts0, 129850),     # SL hit
            _tick(ts0, 129800),     # ignorado, posição fechada
        ]
        run = sim.run(_cfg(), ticks, _make_strategy(at_index=0))
        assert len(run.trades) == 1
        trade = run.trades[0]
        assert trade.risk_decision == "APPROVED_CLOSED_SL"
        # 150 pontos × 0.20 × 1 contrato = R$ 30 de loss
        assert trade.result_gross.amount == Decimal("-30.00")


class TestTakeProfitTrigger:
    def test_long_trade_hits_take_profit(self):
        sim = BacktestSimulator()
        ts0 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        # Entry @ 130000, TP = 300 pontos → fecha quando preço ≥ 130300
        ticks = [
            _tick(ts0, 130000),
            _tick(ts0, 130100),
            _tick(ts0, 130300),     # TP hit
            _tick(ts0, 130500),     # ignorado
        ]
        run = sim.run(_cfg(tp_points="300"), ticks, _make_strategy(at_index=0))
        assert len(run.trades) == 1
        trade = run.trades[0]
        assert trade.risk_decision == "APPROVED_CLOSED_TP"
        # 300 pontos × 0.20 × 1 contrato = R$ 60 de profit
        assert trade.result_gross.amount == Decimal("60.00")
        # Net = gross - brokerage(2.50) - IR(20% sobre 60) = 60 - 2.50 - 12 = 45.50
        assert trade.result_net.amount == Decimal("45.50")


class TestEndOfDayClose:
    def test_position_closes_at_last_tick_if_no_sl_tp(self):
        sim = BacktestSimulator()
        ts0 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        ticks = [
            _tick(ts0, 130000),     # entry (long)
            _tick(ts0, 130050),
            _tick(ts0, 130070),     # último tick — fecha aqui
        ]
        run = sim.run(_cfg(), ticks, _make_strategy(at_index=0))
        assert len(run.trades) == 1
        trade = run.trades[0]
        assert trade.risk_decision == "APPROVED_CLOSED_EOD"
        # 70 pontos × 0.20 = R$ 14
        assert trade.result_gross.amount == Decimal("14.00")


class TestOverlapPrevention:
    def test_simulator_does_not_open_second_position_while_first_open(self):
        sim = BacktestSimulator()
        ts0 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        # Estratégia tenta abrir em todos os ticks
        always = lambda t: OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("150"),
            is_setup_a_plus=True,
        )
        ticks = [
            _tick(ts0, 130000),
            _tick(ts0, 130100),
            _tick(ts0, 130200),
        ]
        run = sim.run(_cfg(), ticks, always)
        # Apenas 1 posição (fechada no EOD)
        approved = [t for t in run.trades
                    if t.risk_decision.startswith("APPROVED")]
        assert len(approved) == 1


class TestRunPersistence:
    def test_run_id_present_and_status_completed(self):
        sim = BacktestSimulator()
        ts0 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        ticks = [_tick(ts0, 130000)]
        run = sim.run(_cfg(), ticks, lambda t: None)
        assert run.id
        assert run.status == "COMPLETED"
        assert run.config.strategy_name == "test"
