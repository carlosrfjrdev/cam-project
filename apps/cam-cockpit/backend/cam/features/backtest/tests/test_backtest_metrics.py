"""
T-F02 — Testes de métricas e walk-forward do Backtest Engine.
TDD First: estes testes foram escritos antes da implementação.
"""
from decimal import Decimal


def make_trade(net: str):
    from cam._shared.domain.primitives import Money
    from cam.features.backtest.domain import BacktestTrade
    gross = Decimal(net)
    return BacktestTrade(
        asset="WIN", direction="LONG", contracts=1,
        entry_price=Decimal("130000"), exit_price=Decimal("130000"),
        result_gross=Money(gross), brokerage=Money(Decimal("0")),
    )


class TestBacktestMetrics:
    def test_win_rate_all_winners(self):
        from cam.features.backtest.domain import BacktestMetrics
        trades = [make_trade("100"), make_trade("200"), make_trade("50")]
        m = BacktestMetrics.compute(trades)
        assert m.win_rate == Decimal("1")
        assert m.winning_trades == 3

    def test_win_rate_mixed(self):
        from cam.features.backtest.domain import BacktestMetrics
        trades = [
            make_trade("100"), make_trade("-50"),
            make_trade("200"), make_trade("-30"),
        ]
        m = BacktestMetrics.compute(trades)
        assert m.win_rate == Decimal("0.5")

    def test_max_drawdown_computed(self):
        from cam.features.backtest.domain import BacktestMetrics
        # Equity: +100, +50, -200, +50 → peak=150, then drops to 0 → dd=150
        trades = [
            make_trade("100"), make_trade("50"),
            make_trade("-200"), make_trade("50"),
        ]
        m = BacktestMetrics.compute(trades)
        assert m.max_drawdown.amount > Decimal("0")

    def test_empty_trades_returns_zeros(self):
        from cam.features.backtest.domain import BacktestMetrics
        m = BacktestMetrics.compute([])
        assert m.total_trades == 0
        assert m.win_rate == Decimal("0")

    def test_profit_factor_no_losses(self):
        from cam.features.backtest.domain import BacktestMetrics
        trades = [make_trade("100"), make_trade("200")]
        m = BacktestMetrics.compute(trades)
        assert m.profit_factor == Decimal("999")


class TestWalkForward:
    def test_walk_forward_splits_window(self):
        from cam.features.backtest.walk_forward import WalkForwardRunner
        ticks = [{"price": 130000 + i, "timestamp": None} for i in range(100)]
        runner = WalkForwardRunner(optimization_pct=0.7, validation_pct=0.3)
        splits = runner.split(ticks)
        assert len(splits) == 1
        opt_len, val_len = len(splits[0][0]), len(splits[0][1])
        assert opt_len == 70
        assert val_len == 30
