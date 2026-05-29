"""
T-B01 — Testes base do Risk Engine.

Valida que a estrutura de tipos, contratos e pipeline vazio estão corretos.
Esses testes devem FALHAR antes da implementação (Red) e passar depois (Green).
"""
from decimal import Decimal

import pytest


class TestRiskEngineImports:
    def test_importable(self):
        from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate

        assert callable(validate)

    def test_approved_type(self):
        from cam._shared.risk import Approved

        result = Approved()
        assert result.approved is True

    def test_rejected_has_reason(self):
        from cam._shared.risk import Rejected

        r = Rejected(reason="test reason", validator="test_validator")
        assert r.approved is False
        assert r.reason == "test reason"
        assert r.validator == "test_validator"

    def test_approved_and_rejected_are_distinct(self):
        from cam._shared.risk import Approved, Rejected

        a = Approved()
        r = Rejected(reason="x", validator="y")
        assert a.approved is True
        assert r.approved is False

    def test_approved_is_frozen(self):
        from cam._shared.risk import Approved

        a = Approved()
        with pytest.raises((AttributeError, TypeError)):
            a.approved = False  # type: ignore[misc]

    def test_rejected_is_frozen(self):
        from cam._shared.risk import Rejected

        r = Rejected(reason="x", validator="y")
        with pytest.raises((AttributeError, TypeError)):
            r.reason = "changed"  # type: ignore[misc]


class TestOrderCandidateAndRiskContext:
    def test_order_candidate_fields(self):
        from cam._shared.domain.primitives import AssetType, ContractCount, Direction
        from cam._shared.risk import OrderCandidate

        c = OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("200"),
        )
        assert c.asset == AssetType.WIN
        assert c.direction == Direction.LONG
        assert c.contracts == ContractCount(1)
        assert c.intended_stop_loss_points == Decimal("200")
        assert c.is_setup_a_plus is False  # default

    def test_order_candidate_setup_a_plus_default(self):
        from cam._shared.domain.primitives import AssetType, ContractCount, Direction
        from cam._shared.risk import OrderCandidate

        c = OrderCandidate(
            asset=AssetType.WDO,
            direction=Direction.SHORT,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("10"),
        )
        assert c.is_setup_a_plus is False

    def test_risk_context_fields(self):
        from cam._shared.domain.primitives import Money, Phase
        from cam._shared.risk import RiskContext

        ctx = RiskContext(
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
        )
        assert ctx.kill_switch_active is False
        assert ctx.phase == Phase.FASE_1
        assert ctx.tax_compliance_ok is True
        assert ctx.open_positions == []
        assert ctx.strategy_authorized_for_phase is True
        assert ctx.circuit_breaker_triggered is False
        assert ctx.current_time is None


class TestEmptyPipeline:
    def test_empty_pipeline_approves_valid_context(self):
        """Pipeline com validators zerados retorna Approved para contexto limpo.

        Este teste valida o 'happy path' mínimo antes de qualquer validator existir.
        Conforme CA1.9.
        """
        from cam._shared.domain.primitives import (
            AssetType,
            ContractCount,
            Direction,
            Money,
            Phase,
        )
        from cam._shared.risk import Approved, OrderCandidate, RiskContext, validate

        ctx = RiskContext(
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
        )
        candidate = OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("200"),
        )
        result = validate(candidate, ctx)
        assert isinstance(result, Approved)

    def test_validate_returns_risk_decision(self):
        from cam._shared.domain.primitives import (
            AssetType,
            ContractCount,
            Direction,
            Money,
            Phase,
        )
        from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate

        ctx = RiskContext(
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
        )
        candidate = OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("200"),
        )
        result = validate(candidate, ctx)
        assert isinstance(result, (Approved, Rejected))
