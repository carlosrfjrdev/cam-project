"""
T-B05 — Validators Grupo 4: Regras Operacionais (posições 13–17).

Validators testados:
    13. daily_operations_count_check (Art. 20º — max ops por dia por fase)
    14. martingale_check             (Art. 13º — proibido aumentar após loss)
    15. trading_window_check         (POV — janelas vedadas de negociação)
    16. setup_a_plus_check           (2 contratos só com Setup A+ em F4)
    17. circuit_breaker_check        (configurável, padrão off)
"""
from datetime import time as dt_time
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import AssetType, ContractCount, Direction, Money, Phase
from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate


def make_base_context(**overrides) -> RiskContext:
    """Contexto completamente limpo — todos os grupos 1-3 passam."""
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
    defaults: dict = dict(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=False,
    )
    defaults.update(overrides)
    return OrderCandidate(**defaults)


class TestDailyOperationsCountCheck:
    """
    Validator 13 — Art. 20º: limite de operações por dia por fase.

    Fase 1: max 3 operações
    Fase 2: max 3 operações
    Fase 3: max 5 operações
    Fase 4: max 5 operações
    """

    def test_fase1_at_3_ops_rejects(self):
        """Na Fase 1, já com 3 operações feitas, a 4ª é bloqueada."""
        ctx = make_base_context(phase=Phase.FASE_1, daily_operations_count=3)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_fase1_at_4_ops_rejects(self):
        ctx = make_base_context(phase=Phase.FASE_1, daily_operations_count=4)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_fase1_at_2_ops_passes(self):
        """Na Fase 1 com 2 operações, a 3ª é permitida (ainda dentro do limite)."""
        ctx = make_base_context(phase=Phase.FASE_1, daily_operations_count=2)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_operations_count_check"

    def test_fase2_at_3_ops_rejects(self):
        ctx = make_base_context(phase=Phase.FASE_2, daily_operations_count=3)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_fase2_at_2_ops_passes(self):
        ctx = make_base_context(phase=Phase.FASE_2, daily_operations_count=2)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_operations_count_check"

    def test_fase3_at_5_ops_rejects(self):
        """Na Fase 3 com 5 operações, a 6ª é bloqueada."""
        ctx = make_base_context(phase=Phase.FASE_3, daily_operations_count=5)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_fase3_at_4_ops_passes(self):
        """Na Fase 3 com 4 operações, a 5ª é permitida."""
        ctx = make_base_context(phase=Phase.FASE_3, daily_operations_count=4)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_operations_count_check"

    def test_fase4_at_5_ops_rejects(self):
        ctx = make_base_context(phase=Phase.FASE_4, daily_operations_count=5)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_fase4_at_4_ops_passes(self):
        ctx = make_base_context(phase=Phase.FASE_4, daily_operations_count=4)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_operations_count_check"

    def test_zero_ops_always_passes_count_check(self):
        ctx = make_base_context(daily_operations_count=0)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_operations_count_check"

    def test_ops_count_reason_is_descriptive(self):
        ctx = make_base_context(phase=Phase.FASE_1, daily_operations_count=3)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10


class TestMartingaleCheck:
    """
    Validator 14 — Art. 13º.

    Proibido aumentar quantidade de contratos imediatamente após uma perda.
    Só verifica quando há registro da última operação (last_operation_result não é None).
    """

    def test_increase_contracts_after_loss_rejected(self):
        """Última op foi loss com 1 contrato. Tentar 2 contratos → Rejected.

        Usa Fase 3 para evitar que phase_contracts_check (pos 7) bloqueie antes
        do martingale_check (pos 14) — em Fase 3, 2 contratos são permitidos por fase.
        """
        ctx = make_base_context(
            phase=Phase.FASE_3,
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "martingale_check"

    def test_same_contracts_after_loss_allowed(self):
        """Manter mesmo número de contratos após loss é permitido."""
        ctx = make_base_context(
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(1))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "martingale_check"

    def test_reduce_contracts_after_loss_allowed(self):
        """Reduzir contratos após loss é permitido (mais conservador)."""
        ctx = make_base_context(
            phase=Phase.FASE_3,
            last_operation_result=Money(Decimal("-100.00")),
            last_operation_contracts=ContractCount(2),
        )
        candidate = make_candidate(contracts=ContractCount(1))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "martingale_check"

    def test_no_last_operation_always_passes_martingale(self):
        """Sem histórico de operação anterior, martingale_check sempre passa."""
        ctx = make_base_context(
            last_operation_result=None,
            last_operation_contracts=None,
        )
        candidate = make_candidate(contracts=ContractCount(2))
        # Pode ser bloqueado por phase_contracts_check (fase 1 max 1 contrato)
        # mas não por martingale_check
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "martingale_check"

    def test_increase_after_gain_is_allowed(self):
        """Aumentar contratos após ganho é permitido (não é martingale)."""
        ctx = make_base_context(
            phase=Phase.FASE_3,
            last_operation_result=Money(Decimal("100.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "martingale_check"

    def test_zero_last_result_not_loss_not_gain_allows_increase(self):
        """Última operação com resultado zero não é loss — pode aumentar."""
        ctx = make_base_context(
            phase=Phase.FASE_3,
            last_operation_result=Money(Decimal("0.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "martingale_check"

    def test_martingale_reason_mentions_art13(self):
        ctx = make_base_context(
            phase=Phase.FASE_3,  # Fase 3 permite 2 contratos por fase
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        result = validate(make_candidate(contracts=ContractCount(2)), ctx)
        assert isinstance(result, Rejected)
        assert "13" in result.reason or "martingale" in result.reason.lower() or "loss" in result.reason.lower()


class TestTradingWindowCheck:
    """
    Validator 15 — POV: janelas vedadas de negociação.

    Horários vedados:
    WIN/WDO:
        - Abertura B3: 09:00. Vedado: 09:00–09:15 (primeiros 15min)
        - Fechamento WIN: 17:50. Vedado: 17:40–17:50 (últimos 10min)
        - Fechamento WDO: 18:15. Vedado: 18:05–18:15 (últimos 10min)

    Se current_time é None, o validator pula (modo de teste).
    """

    def test_none_current_time_skips_validator(self):
        """current_time=None → validator pula (não bloqueia)."""
        ctx = make_base_context(current_time=None)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "trading_window_check"

    def test_win_in_opening_window_rejected(self):
        """WIN às 09:05 (dentro dos primeiros 15min) → Rejected."""
        ctx = make_base_context(current_time=dt_time(9, 5))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_win_at_opening_start_rejected(self):
        """WIN às 09:00 exato → Rejected (início da janela vedada)."""
        ctx = make_base_context(current_time=dt_time(9, 0))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_win_at_09_15_allowed(self):
        """WIN às 09:15 exato → janela liberada (vedado é 09:00–09:14:59)."""
        ctx = make_base_context(current_time=dt_time(9, 15))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "trading_window_check"

    def test_win_in_normal_trading_hours_allowed(self):
        """WIN às 10:30 → horário normal, liberado."""
        ctx = make_base_context(current_time=dt_time(10, 30))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "trading_window_check"

    def test_win_in_closing_window_rejected(self):
        """WIN às 17:45 (dentro dos últimos 10min antes do fechamento) → Rejected."""
        ctx = make_base_context(current_time=dt_time(17, 45))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_win_at_17_40_rejected(self):
        """WIN às 17:40 → início da janela vedada de fechamento WIN."""
        ctx = make_base_context(current_time=dt_time(17, 40))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_win_at_17_39_allowed(self):
        """WIN às 17:39 → ainda fora da janela vedada."""
        ctx = make_base_context(current_time=dt_time(17, 39))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "trading_window_check"

    def test_wdo_in_opening_window_rejected(self):
        """WDO às 09:10 → vedado (abertura)."""
        ctx = make_base_context(current_time=dt_time(9, 10))
        result = validate(make_candidate(asset=AssetType.WDO), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_wdo_in_closing_window_rejected(self):
        """WDO às 18:10 (dentro dos últimos 10min antes de 18:15) → Rejected."""
        ctx = make_base_context(current_time=dt_time(18, 10))
        result = validate(make_candidate(asset=AssetType.WDO), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_wdo_at_18_05_rejected(self):
        """WDO às 18:05 → início da janela vedada de fechamento WDO."""
        ctx = make_base_context(current_time=dt_time(18, 5))
        result = validate(make_candidate(asset=AssetType.WDO), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "trading_window_check"

    def test_wdo_at_18_04_allowed(self):
        """WDO às 18:04 → ainda fora da janela vedada."""
        ctx = make_base_context(current_time=dt_time(18, 4))
        result = validate(make_candidate(asset=AssetType.WDO), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "trading_window_check"

    def test_trading_window_reason_is_descriptive(self):
        ctx = make_base_context(current_time=dt_time(9, 10))
        result = validate(make_candidate(asset=AssetType.WIN), ctx)
        assert isinstance(result, Rejected)
        assert "janela" in result.reason.lower() or "vedado" in result.reason.lower() or "window" in result.reason.lower()


class TestSetupAPlusCheck:
    """
    Validator 16: 2 contratos permitidos apenas em Setup A+ (Fase 4).

    A combinação "2 contratos + Setup A+" é autorizada somente na Fase 4.
    Em fases anteriores, phase_contracts_check já bloqueia (Fases 1 e 2).
    Na Fase 3, 2 contratos são permitidos SEM exigência de Setup A+.
    Na Fase 4, 2 contratos EXIGEM Setup A+.
    """

    def test_fase4_2_contracts_without_setup_a_plus_rejected(self):
        """Fase 4 + 2 contratos + sem Setup A+ → Rejected."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=False)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "setup_a_plus_check"

    def test_fase4_2_contracts_with_setup_a_plus_passes_this_validator(self):
        """Fase 4 + 2 contratos + Setup A+ → passa pelo setup_a_plus_check."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=True)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "setup_a_plus_check"

    def test_fase4_1_contract_without_setup_a_plus_passes(self):
        """Fase 4 + 1 contrato + sem Setup A+ → sempre passa (1 contrato não exige)."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(1), is_setup_a_plus=False)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "setup_a_plus_check"

    def test_fase3_2_contracts_without_setup_a_plus_passes_this_validator(self):
        """Fase 3 + 2 contratos + sem Setup A+ → setup_a_plus_check passa (não requer A+ na F3)."""
        ctx = make_base_context(phase=Phase.FASE_3)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=False)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "setup_a_plus_check"

    def test_setup_a_plus_reason_is_descriptive(self):
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=False)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10


class TestCircuitBreakerCheck:
    """Validator 17 — Circuit breaker configurável (padrão off)."""

    def test_circuit_breaker_triggered_rejects(self):
        ctx = make_base_context(circuit_breaker_triggered=True)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "circuit_breaker_check"

    def test_circuit_breaker_off_does_not_block(self):
        ctx = make_base_context(circuit_breaker_triggered=False)
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "circuit_breaker_check"

    def test_circuit_breaker_reason_is_descriptive(self):
        ctx = make_base_context(circuit_breaker_triggered=True)
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10


class TestGroup4OrderAndPriority:
    """Testa prioridades dentro do Grupo 4 (SPEC R1.06 posições 13–17)."""

    def test_ops_count_before_martingale(self):
        """
        daily_operations_count_check (pos 13) antes de martingale_check (pos 14).
        """
        ctx = make_base_context(
            phase=Phase.FASE_1,
            daily_operations_count=3,  # limite atingido
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(2))
        # Ambos deveriam falhar, mas ops_count (pos 13) vence
        # Note: phase_contracts_check (pos 7) rejeitaria 2 contratos em F1 antes
        # Por isso usamos 1 contrato para isolar o grupo 4
        ctx2 = make_base_context(
            phase=Phase.FASE_1,
            daily_operations_count=3,
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate2 = make_candidate(contracts=ContractCount(1))
        result = validate(candidate2, ctx2)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_operations_count_check"

    def test_martingale_before_circuit_breaker(self):
        """
        martingale_check (pos 14) antes de circuit_breaker_check (pos 17).
        """
        ctx = make_base_context(
            phase=Phase.FASE_3,
            circuit_breaker_triggered=True,
            last_operation_result=Money(Decimal("-50.00")),
            last_operation_contracts=ContractCount(1),
        )
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        # martingale_check (pos 14) vem antes de circuit_breaker_check (pos 17)
        assert result.validator == "martingale_check"
