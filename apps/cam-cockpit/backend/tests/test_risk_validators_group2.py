"""
T-B03 — Validators Grupo 2: Limites de Contratos e Posição (posições 6–8).

Validators testados:
    6. max_contracts_check         (Art. 11º — INTOCÁVEL, hardcoded)
    7. phase_contracts_check       (Art. 12º — limites por fase)
    8. simultaneous_position_check (Art. 12º — WIN+WDO simultâneo vedado em F1/F2)

INVARIANTE CONSTITUCIONAL (Art. 11º):
    MAX_WIN_CONTRACTS = 2  — hardcoded, nunca ler de config/banco/env
    MAX_WDO_CONTRACTS = 2  — hardcoded, nunca ler de config/banco/env

    Nenhum parâmetro, nenhuma POV, nenhuma configuração pode sobrescrever esse limite.
    Testes verificam esse invariante de forma explícita.
"""
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    OpenPosition,
    Phase,
)
from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate


def make_base_context(**overrides) -> RiskContext:
    """Contexto completamente limpo — Grupo 1 passa, sem posições abertas."""
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
    """Candidato padrão: 1 contrato WIN LONG."""
    defaults: dict = dict(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=False,
    )
    defaults.update(overrides)
    return OrderCandidate(**defaults)


class TestMaxContractsCheck:
    """
    Validator 6 — Art. 11º — INTOCÁVEL.

    O limite de 2 contratos é hardcoded. Nenhuma condição, fase,
    POV, parâmetro ou configuração pode sobrescrever.
    """

    def test_3_win_contracts_always_rejected(self):
        """Art. 11º: 3 WIN sempre rejeitado, sem exceção."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(
            asset=AssetType.WIN,
            contracts=ContractCount(3),
            is_setup_a_plus=True,
        )
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "max_contracts_check"

    def test_3_wdo_contracts_always_rejected(self):
        """Art. 11º: 3 WDO sempre rejeitado, sem exceção."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(
            asset=AssetType.WDO,
            contracts=ContractCount(3),
            is_setup_a_plus=True,
        )
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "max_contracts_check"

    def test_10_contracts_always_rejected(self):
        """Qualquer quantidade > 2 é sempre rejeitada."""
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(10), is_setup_a_plus=True)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "max_contracts_check"

    def test_max_contracts_reason_mentions_art11(self):
        ctx = make_base_context()
        candidate = make_candidate(contracts=ContractCount(3))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert "11" in result.reason or "contrato" in result.reason.lower()

    def test_2_win_contracts_not_blocked_by_max_contracts_check(self):
        """2 contratos WIN não deve ser bloqueado por max_contracts_check (pode ser por outros)."""
        # Usamos Fase 4 para minimizar bloqueios de outros validators de fase
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(
            asset=AssetType.WIN,
            contracts=ContractCount(2),
            is_setup_a_plus=True,
        )
        result = validate(candidate, ctx)
        # O resultado pode ser Approved ou Rejected por outro validator, mas NÃO por max_contracts_check
        if isinstance(result, Rejected):
            assert result.validator != "max_contracts_check"

    def test_2_wdo_contracts_not_blocked_by_max_contracts_check(self):
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(
            asset=AssetType.WDO,
            contracts=ContractCount(2),
            is_setup_a_plus=True,
        )
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "max_contracts_check"

    def test_1_contract_not_blocked_by_max_contracts_check(self):
        """1 contrato nunca é bloqueado por max_contracts_check."""
        ctx = make_base_context()
        candidate = make_candidate(contracts=ContractCount(1))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "max_contracts_check"

    def test_max_contracts_check_before_phase_contracts_check(self):
        """
        max_contracts_check (pos 6) tem prioridade sobre phase_contracts_check (pos 7).
        Se ambos falhariam, o pos 6 vence.
        """
        # Em Fase 1, max 1 contrato. Mas 3 contratos viola Art. 11º primeiro.
        ctx = make_base_context(phase=Phase.FASE_1)
        candidate = make_candidate(contracts=ContractCount(3))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "max_contracts_check"


class TestPhaseContractsCheck:
    """
    Validator 7 — Art. 12º: limites de contratos por fase.

    Fase 1: max 1 contrato (paper trading)
    Fase 2: max 1 contrato (primeiro real)
    Fase 3: max 2 contratos (consolidação)
    Fase 4: max 2 contratos com Setup A+ confirmado
    """

    def test_fase1_max_1_contract_2_rejected(self):
        ctx = make_base_context(phase=Phase.FASE_1)
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "phase_contracts_check"

    def test_fase2_max_1_contract_2_rejected(self):
        ctx = make_base_context(phase=Phase.FASE_2)
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "phase_contracts_check"

    def test_fase1_1_contract_passes_phase_contracts_check(self):
        ctx = make_base_context(phase=Phase.FASE_1)
        candidate = make_candidate(contracts=ContractCount(1))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "phase_contracts_check"

    def test_fase2_1_contract_passes_phase_contracts_check(self):
        ctx = make_base_context(phase=Phase.FASE_2)
        candidate = make_candidate(contracts=ContractCount(1))
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "phase_contracts_check"

    def test_fase3_2_contracts_passes_phase_contracts_check(self):
        """Fase 3 permite 2 contratos sem exigir Setup A+."""
        ctx = make_base_context(phase=Phase.FASE_3)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=False)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "phase_contracts_check"

    def test_fase4_2_contracts_with_setup_a_plus_passes_phase_contracts_check(self):
        ctx = make_base_context(phase=Phase.FASE_4)
        candidate = make_candidate(contracts=ContractCount(2), is_setup_a_plus=True)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "phase_contracts_check"

    def test_phase_contracts_reason_mentions_phase(self):
        ctx = make_base_context(phase=Phase.FASE_1)
        candidate = make_candidate(contracts=ContractCount(2))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "phase_contracts_check"
        assert len(result.reason) > 10


class TestSimultaneousPositionCheck:
    """
    Validator 8 — Art. 12º: WIN+WDO simultâneo vedado em Fases 1 e 2.

    Nas fases iniciais (1 e 2), o operador não pode ter posição WIN
    e tentar abrir WDO ao mesmo tempo, e vice-versa.
    Fase 3 e 4 permitem simultâneo (dentro dos limites de contratos).
    """

    def test_win_position_open_trying_wdo_fase1_rejected(self):
        """Posição WIN aberta + candidato WDO em Fase 1 = Rejected."""
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WDO)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "simultaneous_position_check"

    def test_wdo_position_open_trying_win_fase1_rejected(self):
        """Posição WDO aberta + candidato WIN em Fase 1 = Rejected."""
        existing_wdo = OpenPosition(
            asset=AssetType.WDO,
            contracts=ContractCount(1),
            direction=Direction.SHORT,
            entry_price=Decimal("5200"),
        )
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[existing_wdo])
        candidate = make_candidate(asset=AssetType.WIN)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "simultaneous_position_check"

    def test_win_position_open_trying_wdo_fase2_rejected(self):
        """Fase 2 também veda WIN+WDO simultâneo."""
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_2, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WDO)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "simultaneous_position_check"

    def test_win_position_open_trying_wdo_fase3_allowed(self):
        """Fase 3 permite WIN+WDO simultâneo."""
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_3, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WDO)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "simultaneous_position_check"

    def test_no_open_positions_always_passes_this_validator(self):
        """Sem posições abertas, simultaneous_position_check sempre passa."""
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[])
        candidate = make_candidate(asset=AssetType.WIN)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "simultaneous_position_check"

    def test_same_asset_open_position_does_not_trigger_simultaneous(self):
        """Posição WIN aberta + candidato WIN: não é simultâneo WIN+WDO."""
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WIN)
        result = validate(candidate, ctx)
        if isinstance(result, Rejected):
            assert result.validator != "simultaneous_position_check"

    def test_simultaneous_reason_is_descriptive(self):
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WDO)
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert len(result.reason) > 10


class TestGroup2OrderAndPriority:
    """Testa a ordem dos validators do Grupo 2 (SPEC R1.06 posições 6–8)."""

    def test_max_contracts_before_simultaneous_check(self):
        """
        max_contracts_check (pos 6) tem prioridade sobre simultaneous_position_check (pos 8).
        3 contratos WDO com WIN aberto: rejeita por Art. 11º, não por simultâneo.
        """
        existing_win = OpenPosition(
            asset=AssetType.WIN,
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("130000"),
        )
        ctx = make_base_context(phase=Phase.FASE_1, open_positions=[existing_win])
        candidate = make_candidate(asset=AssetType.WDO, contracts=ContractCount(3))
        result = validate(candidate, ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "max_contracts_check"
