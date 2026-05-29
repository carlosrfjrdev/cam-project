"""
T-B02 — Validators Grupo 1: Guardas de Estado (posições 1–5 do pipeline).

Validators testados:
    1. kill_switch_active_check   (Art. 18º)
    2. pre_market_checklist_check (Art. 32º)
    3. post_market_checklist_check(Art. 33º)
    4. tax_compliance_check       (Art. 26º)
    5. phase_authorization_check  (Art. 30º)

Todos os testes devem FALHAR antes da implementação (Red).
"""
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import AssetType, ContractCount, Direction, Money, Phase
from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate


def make_base_context(**overrides) -> RiskContext:
    """Contexto completamente limpo — todos os validators devem passar."""
    defaults: dict = dict(
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
    """Candidato válido padrão — 1 contrato WIN LONG."""
    defaults: dict = dict(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=False,
    )
    defaults.update(overrides)
    return OrderCandidate(**defaults)


class TestKillSwitchCheck:
    """Validator 1 — Art. 18º: kill switch bloqueia tudo imediatamente."""

    def test_kill_switch_active_rejects(self):
        ctx = make_base_context(kill_switch_active=True)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"

    def test_kill_switch_active_reason_mentions_art18(self):
        ctx = make_base_context(kill_switch_active=True)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        # Motivo deve mencionar kill switch ou Art. 18º
        reason_lower = result.reason.lower()
        assert "kill switch" in reason_lower or "18" in result.reason

    def test_kill_switch_inactive_does_not_block(self):
        ctx = make_base_context(kill_switch_active=False)
        result = validate(make_candidate(), ctx)
        # Com contexto limpo e kill switch off, não deve ser bloqueado por este validator
        if isinstance(result, Rejected):
            assert result.validator != "kill_switch_active_check"

    def test_kill_switch_true_blocks_even_with_valid_everything_else(self):
        """Kill switch prevalece sobre qualquer outra condição favorável."""
        ctx = make_base_context(
            kill_switch_active=True,
            pre_market_checklist_done=True,
            post_market_checklist_done=True,
            tax_compliance_ok=True,
            strategy_authorized_for_phase=True,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"


class TestPreMarketChecklistCheck:
    """Validator 2 — Art. 32º: checklist pré-mercado do dia deve estar preenchido."""

    def test_missing_pre_market_checklist_rejects(self):
        ctx = make_base_context(pre_market_checklist_done=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "pre_market_checklist_check"

    def test_missing_pre_market_reason_is_descriptive(self):
        ctx = make_base_context(pre_market_checklist_done=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10

    def test_pre_market_done_does_not_block_this_validator(self):
        ctx = make_base_context(pre_market_checklist_done=True)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "pre_market_checklist_check"


class TestPostMarketChecklistCheck:
    """Validator 3 — Art. 33º: checklist pós-mercado do pregão anterior deve existir."""

    def test_missing_post_market_checklist_rejects(self):
        ctx = make_base_context(post_market_checklist_done=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "post_market_checklist_check"

    def test_missing_post_market_reason_is_descriptive(self):
        ctx = make_base_context(post_market_checklist_done=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10

    def test_post_market_done_does_not_block_this_validator(self):
        ctx = make_base_context(post_market_checklist_done=True)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "post_market_checklist_check"


class TestTaxComplianceCheck:
    """Validator 4 — Art. 26º: DARF atrasada bloqueia novas operações."""

    def test_darf_overdue_rejects(self):
        ctx = make_base_context(tax_compliance_ok=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "tax_compliance_check"

    def test_darf_overdue_reason_mentions_darf_or_fiscal(self):
        ctx = make_base_context(tax_compliance_ok=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        reason_upper = result.reason.upper()
        assert "DARF" in reason_upper or "FISCAL" in reason_upper or "26" in result.reason

    def test_tax_compliant_does_not_block_this_validator(self):
        ctx = make_base_context(tax_compliance_ok=True)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "tax_compliance_check"


class TestPhaseAuthorizationCheck:
    """Validator 5 — Art. 30º: estratégia deve estar autorizada na fase atual."""

    def test_unauthorized_strategy_rejects(self):
        ctx = make_base_context(strategy_authorized_for_phase=False)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "phase_authorization_check"

    def test_unauthorized_strategy_reason_mentions_fase(self):
        ctx = make_base_context(strategy_authorized_for_phase=False, phase=Phase.FASE_2)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        # Motivo deve mencionar fase ou autorização
        reason_lower = result.reason.lower()
        assert "fase" in reason_lower or "autoriza" in reason_lower or "FASE" in result.reason

    def test_authorized_strategy_does_not_block_this_validator(self):
        ctx = make_base_context(strategy_authorized_for_phase=True)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "phase_authorization_check"


class TestGroup1OrderAndPriority:
    """Testa que a ordem dos validators do Grupo 1 é respeitada (SPEC R1.06)."""

    def test_kill_switch_has_priority_over_pre_market_checklist(self):
        """
        Kill switch (pos 1) deve ser rejeitado ANTES de checklist pré-mercado (pos 2).
        Se ambos falharem, o validator 1 vence.
        """
        ctx = make_base_context(
            kill_switch_active=True,
            pre_market_checklist_done=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"

    def test_kill_switch_has_priority_over_post_market_checklist(self):
        ctx = make_base_context(
            kill_switch_active=True,
            post_market_checklist_done=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"

    def test_kill_switch_has_priority_over_tax_compliance(self):
        ctx = make_base_context(
            kill_switch_active=True,
            tax_compliance_ok=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"

    def test_kill_switch_has_priority_over_all_other_group1_failures(self):
        ctx = make_base_context(
            kill_switch_active=True,
            pre_market_checklist_done=False,
            post_market_checklist_done=False,
            tax_compliance_ok=False,
            strategy_authorized_for_phase=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "kill_switch_active_check"

    def test_pre_market_has_priority_over_post_market_when_kill_switch_off(self):
        """Com kill switch off, pre_market (pos 2) tem prioridade sobre post_market (pos 3)."""
        ctx = make_base_context(
            kill_switch_active=False,
            pre_market_checklist_done=False,
            post_market_checklist_done=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "pre_market_checklist_check"

    def test_pre_market_has_priority_over_tax_compliance(self):
        ctx = make_base_context(
            kill_switch_active=False,
            pre_market_checklist_done=False,
            tax_compliance_ok=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "pre_market_checklist_check"

    def test_post_market_has_priority_over_tax_compliance(self):
        ctx = make_base_context(
            kill_switch_active=False,
            pre_market_checklist_done=True,
            post_market_checklist_done=False,
            tax_compliance_ok=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "post_market_checklist_check"

    def test_tax_compliance_has_priority_over_phase_authorization(self):
        ctx = make_base_context(
            kill_switch_active=False,
            pre_market_checklist_done=True,
            post_market_checklist_done=True,
            tax_compliance_ok=False,
            strategy_authorized_for_phase=False,
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "tax_compliance_check"

    def test_clean_group1_context_does_not_reject_in_group1(self):
        """Contexto limpo não deve ser rejeitado por nenhum validator do Grupo 1."""
        ctx = make_base_context()
        result = validate(make_candidate(), ctx)
        # Com contexto 100% limpo, não deve haver rejeição de nenhum validator do Grupo 1
        if isinstance(result, Rejected):
            assert result.validator not in [
                "kill_switch_active_check",
                "pre_market_checklist_check",
                "post_market_checklist_check",
                "tax_compliance_check",
                "phase_authorization_check",
            ]
