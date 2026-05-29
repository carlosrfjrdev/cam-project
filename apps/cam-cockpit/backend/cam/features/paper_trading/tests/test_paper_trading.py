"""
Testes TDD First — paper trading backend (T-H01).

Garante:
- Risk Engine sempre ativo (CA5.5)
- paper trades NAO persistem em cam_journal_entries (tabela de producao)
- todas as regras constitucionais ativas no paper trading
"""
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    Phase,
)
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam.features.paper_trading.domain import PaperTrade, PaperTradeStatus
from cam.features.paper_trading.service import PaperTradingService


def make_context(**overrides) -> RiskContext:
    defaults = dict(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000.00")),
        daily_pnl=Money(Decimal("0.00")),
        weekly_pnl=Money(Decimal("0.00")),
        monthly_pnl=Money(Decimal("0.00")),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
        strategy_authorized_for_phase=True,
        circuit_breaker_triggered=False,
        current_time=None,
    )
    defaults.update(overrides)
    return RiskContext(**defaults)


def make_candidate(**overrides) -> OrderCandidate:
    defaults = dict(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("150"),
    )
    defaults.update(overrides)
    return OrderCandidate(**defaults)


class TestPaperTradingService:
    def test_simulate_returns_paper_trade(self):
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context()
        result = svc.simulate(candidate, ctx)
        assert isinstance(result, PaperTrade)

    def test_approved_when_risk_engine_permits(self):
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context()
        result = svc.simulate(candidate, ctx)
        assert result.status == PaperTradeStatus.APPROVED

    def test_rejected_when_kill_switch_active(self):
        """Art. 18o -- kill switch bloqueia mesmo em paper trading."""
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context(kill_switch_active=True)
        result = svc.simulate(candidate, ctx)
        assert result.status == PaperTradeStatus.REJECTED
        assert result.rejection_reason is not None

    def test_rejected_when_contracts_exceed_limit(self):
        """Art. 11o -- max 2 contratos, intocavel mesmo em paper trading."""
        svc = PaperTradingService()
        candidate = make_candidate(contracts=ContractCount(3))
        ctx = make_context()
        result = svc.simulate(candidate, ctx)
        assert result.status == PaperTradeStatus.REJECTED

    def test_rejected_when_daily_loss_limit_reached(self):
        """3% de loss atingido -- paper trading bloqueado."""
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context(
            total_capital=Money(Decimal("5000.00")),
            daily_pnl=Money(Decimal("-200.00")),  # > 3% de 5000 = 150
        )
        result = svc.simulate(candidate, ctx)
        assert result.status == PaperTradeStatus.REJECTED

    def test_paper_trade_is_marked_as_paper(self):
        """CA5.5 -- trade simulado deve ter flag de paper sempre setada."""
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context()
        result = svc.simulate(candidate, ctx)
        assert result.is_paper is True

    def test_simulated_pnl_for_approved_trade(self):
        svc = PaperTradingService()
        candidate = make_candidate()
        ctx = make_context()
        result = svc.simulate(candidate, ctx, exit_price_points=Decimal("200"))
        assert result.status == PaperTradeStatus.APPROVED
        assert result.simulated_result_gross is not None


class TestPaperTradeDomain:
    def test_paper_trade_has_required_fields(self):
        trade = PaperTrade(
            candidate_asset=AssetType.WIN,
            candidate_direction=Direction.LONG,
            candidate_contracts=ContractCount(1),
            status=PaperTradeStatus.APPROVED,
            is_paper=True,
            rejection_reason=None,
            simulated_result_gross=Money(Decimal("100.00")),
            simulated_result_net=Money(Decimal("80.00")),
        )
        assert trade.is_paper is True
        assert trade.status == PaperTradeStatus.APPROVED

    def test_rejected_trade_has_no_pnl(self):
        trade = PaperTrade(
            candidate_asset=AssetType.WIN,
            candidate_direction=Direction.LONG,
            candidate_contracts=ContractCount(1),
            status=PaperTradeStatus.REJECTED,
            is_paper=True,
            rejection_reason="Kill switch ativo",
            simulated_result_gross=None,
            simulated_result_net=None,
        )
        assert trade.simulated_result_gross is None
        assert trade.rejection_reason == "Kill switch ativo"
