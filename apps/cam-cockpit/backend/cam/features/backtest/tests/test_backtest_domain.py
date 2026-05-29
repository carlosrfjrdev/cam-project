"""
T-F01 — Testes de domínio do Backtest Engine.
TDD First: estes testes foram escritos antes da implementação.
"""
from datetime import UTC, datetime
from decimal import Decimal


class TestBacktestDomain:
    def test_backtest_config_has_required_fields(self):
        from cam._shared.domain.primitives import Phase
        from cam.features.backtest.domain import BacktestConfig
        cfg = BacktestConfig(
            strategy_name="teste_reversal",
            date_from=datetime(2026, 1, 1, tzinfo=UTC),
            date_to=datetime(2026, 5, 1, tzinfo=UTC),
            phase=Phase.FASE_1,
            brokerage_per_contract=Decimal("2.50"),
        )
        assert cfg.strategy_name == "teste_reversal"
        assert cfg.brokerage_per_contract == Decimal("2.50")

    def test_backtest_trade_calculates_net_result(self):
        from cam._shared.domain.primitives import Money
        from cam.features.backtest.domain import BacktestTrade
        trade = BacktestTrade(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130200"),
            result_gross=Money(Decimal("400.00")),
            brokerage=Money(Decimal("5.00")),
        )
        # net = 400 - 5 - (400*0.20) = 400 - 5 - 80 = 315
        assert trade.result_net.amount == Decimal("315.00")
        assert trade.tax_provisioned.amount == Decimal("80.00")

    def test_backtest_trade_no_tax_on_loss(self):
        from cam._shared.domain.primitives import Money
        from cam.features.backtest.domain import BacktestTrade
        trade = BacktestTrade(
            asset="WIN", direction="SHORT", contracts=1,
            entry_price=Decimal("130200"), exit_price=Decimal("130000"),
            result_gross=Money(Decimal("-400.00")),
            brokerage=Money(Decimal("5.00")),
        )
        assert trade.tax_provisioned.amount == Decimal("0.00")
        assert trade.result_net.amount == Decimal("-405.00")

    def test_risk_engine_cannot_be_bypassed(self):
        """CA7.5 — Risk Engine sempre ativo no backtest."""
        from cam.features.backtest import simulator
        source = open(simulator.__file__).read()
        # O simulador nunca deve ter lógica para "skip risk engine"
        assert "skip_risk" not in source.lower()
        assert "bypass" not in source.lower()
        assert "disable_risk" not in source.lower()
