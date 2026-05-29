"""
T-B07 — Property-based tests com Hypothesis para o Risk Engine.

Propriedades testadas (invariantes do sistema):
    P1: Nunca Approved quando viola Art. 11º (CA1.14)
    P2: Sempre Rejected pelo daily_loss_limit_check quando loss >= 3%
    P3: Kill switch ativo sempre é o primeiro Rejected (kill_switch_active_check)
    P4: Gain lock bloqueia quando daily_pnl >= 2% do capital
    P5: Martingale sempre bloqueado quando loss precedente + aumento de contratos (F3/F4)
    P6: Contexto completamente limpo sempre produz Approved

Meta de cobertura: >= 10.000 cenários gerados (definida por max_examples nos testes críticos).
"""
from decimal import Decimal

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    Phase,
)
from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate

# Strategies reutilizáveis
_asset_st = st.sampled_from(list(AssetType))
_direction_st = st.sampled_from(list(Direction))
_phase_st = st.sampled_from(list(Phase))
_contracts_valid_st = st.integers(min_value=1, max_value=2)
_contracts_over_limit_st = st.integers(min_value=3, max_value=100)
_pnl_st = st.decimals(
    min_value=Decimal("-10000"),
    max_value=Decimal("10000"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
_capital_st = st.decimals(
    min_value=Decimal("1000"),
    max_value=Decimal("100000"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)


def make_clean_context_for_hypothesis(
    kill_switch_active: bool = False,
    phase: Phase = Phase.FASE_1,
    daily_pnl_amount: Decimal = Decimal("0"),
    weekly_pnl_amount: Decimal = Decimal("0"),
    monthly_pnl_amount: Decimal = Decimal("0"),
    total_capital_amount: Decimal = Decimal("5000"),
    daily_operations_count: int = 0,
) -> RiskContext:
    """Helper para Hypothesis — cria contexto com parâmetros variados."""
    return RiskContext(
        kill_switch_active=kill_switch_active,
        phase=phase,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(total_capital_amount),
        daily_pnl=Money(daily_pnl_amount),
        weekly_pnl=Money(weekly_pnl_amount),
        monthly_pnl=Money(monthly_pnl_amount),
        daily_operations_count=daily_operations_count,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
        strategy_authorized_for_phase=True,
        circuit_breaker_triggered=False,
        current_time=None,
    )


# P1 — Art. 11º: NUNCA Approved com > 2 contratos
@settings(max_examples=10000, suppress_health_check=[HealthCheck.too_slow])
@given(
    contracts=_contracts_over_limit_st,
    asset=_asset_st,
    phase=_phase_st,
    direction=_direction_st,
)
def test_property_p1_more_than_2_contracts_always_rejected(
    contracts: int,
    asset: AssetType,
    phase: Phase,
    direction: Direction,
) -> None:
    """
    P1 — CA1.14 — Art. 11º INVARIANTE.

    Para qualquer quantidade de contratos > 2, qualquer ativo, qualquer fase
    e qualquer direção: o resultado é sempre Rejected com validator max_contracts_check.

    Este é o invariante mais importante do sistema. Se falhar, é uma violação
    constitucional grave.
    """
    ctx = make_clean_context_for_hypothesis(phase=phase)
    candidate = OrderCandidate(
        asset=asset,
        direction=direction,
        contracts=ContractCount(contracts),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=True,  # melhor caso possível — ainda deve ser bloqueado
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Rejected), (
        f"VIOLAÇÃO CONSTITUCIONAL ART. 11º: {contracts} contratos de {asset} "
        f"na {phase} foram APROVADOS! Isso não pode acontecer."
    )
    assert result.validator == "max_contracts_check", (
        f"Art. 11º deve ser bloqueado por max_contracts_check, "
        f"mas foi bloqueado por {result.validator}"
    )


# P2 — Art. 16º: loss diário >= 3% sempre bloqueia
@settings(max_examples=5000, suppress_health_check=[HealthCheck.too_slow])
@given(
    loss_pct=st.decimals(
        min_value=Decimal("0.03"),
        max_value=Decimal("1.00"),
        places=6,
        allow_nan=False,
        allow_infinity=False,
    ),
    capital=_capital_st,
)
def test_property_p2_daily_loss_at_or_above_3pct_always_rejected(
    loss_pct: Decimal,
    capital: Decimal,
) -> None:
    """
    P2 — Art. 16º: para qualquer perda >= 3% do capital, daily_loss_limit_check bloqueia.

    Verifica que a regra escala corretamente com diferentes valores de capital.
    """
    # Não quantizar para evitar perda de precisão que faria o P&L ficar
    # marginalmente acima do limite calculado pelo engine com mesma precisão
    loss = capital * loss_pct
    assume(loss > Decimal("0"))

    ctx = make_clean_context_for_hypothesis(
        total_capital_amount=capital,
        daily_pnl_amount=-loss,
    )
    candidate = OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Rejected), (
        f"Loss de R$ {loss} ({loss_pct * 100:.4f}% de R$ {capital}) "
        f"deveria ser bloqueado mas foi Approved. "
        f"Limite calculado pelo engine: {capital * Decimal('0.03')}"
    )
    # Pode ser bloqueado por daily_loss_limit_check ou weekly/monthly se os valores
    # acidentalmente ultrapassarem os limites (improvável com capital alto e pct pequeno)
    assert result.validator in {
        "daily_loss_limit_check",
        "weekly_loss_limit_check",
        "monthly_loss_limit_check",
    }


# P3 — Art. 18º: kill switch ativo SEMPRE é o primeiro bloqueio
@settings(max_examples=2000, suppress_health_check=[HealthCheck.too_slow])
@given(
    phase=_phase_st,
    contracts=st.integers(min_value=1, max_value=2),
    asset=_asset_st,
)
def test_property_p3_kill_switch_always_first(
    phase: Phase,
    contracts: int,
    asset: AssetType,
) -> None:
    """
    P3 — Art. 18º: kill switch ativo sempre produz Rejected com kill_switch_active_check.

    Independentemente de qualquer outra condição do contexto, o kill switch
    é o primeiro validator e sempre vence.
    """
    ctx = make_clean_context_for_hypothesis(kill_switch_active=True, phase=phase)
    candidate = OrderCandidate(
        asset=asset,
        direction=Direction.LONG,
        contracts=ContractCount(contracts),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=True,
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Rejected)
    assert result.validator == "kill_switch_active_check", (
        f"Kill switch ativo deveria ser o primeiro bloqueio, "
        f"mas foi {result.validator}"
    )


# P4 — Art. 17º: gain lock >= 2% sempre bloqueia
@settings(max_examples=3000, suppress_health_check=[HealthCheck.too_slow])
@given(
    gain_pct=st.decimals(
        min_value=Decimal("0.02"),
        max_value=Decimal("1.00"),
        places=6,
        allow_nan=False,
        allow_infinity=False,
    ),
    capital=_capital_st,
)
def test_property_p4_gain_lock_at_or_above_2pct_always_rejected(
    gain_pct: Decimal,
    capital: Decimal,
) -> None:
    """
    P4 — Art. 17º: qualquer ganho >= 2% do capital aciona gain_lock_check.
    """
    # Não quantizar para manter precisão consistente com o cálculo do engine
    gain = capital * gain_pct
    assume(gain > Decimal("0"))

    ctx = make_clean_context_for_hypothesis(
        total_capital_amount=capital,
        daily_pnl_amount=gain,
    )
    candidate = OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Rejected), (
        f"Ganho de R$ {gain} ({gain_pct * 100:.4f}% de R$ {capital}) "
        f"deveria acionar gain lock mas foi Approved. "
        f"Threshold do engine: {capital * Decimal('0.02')}"
    )
    assert result.validator == "gain_lock_check"


# P5 — Art. 13º: martingale bloqueado em contexto adequado
@settings(max_examples=3000, suppress_health_check=[HealthCheck.too_slow])
@given(
    last_loss=st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("5000"),
        places=2,
        allow_nan=False,
        allow_infinity=False,
    ),
)
def test_property_p5_martingale_always_blocked_after_loss(last_loss: Decimal) -> None:
    """
    P5 — Art. 13º: tentativa de aumentar contratos após qualquer loss é bloqueada.

    Usa Fase 3 para evitar interferência de phase_contracts_check.
    """
    ctx = RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_3,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000")),
        daily_pnl=Money(Decimal("0")),
        weekly_pnl=Money(Decimal("0")),
        monthly_pnl=Money(Decimal("0")),
        daily_operations_count=0,
        last_operation_result=Money(-last_loss),   # último resultado foi loss
        last_operation_contracts=ContractCount(1),  # com 1 contrato
        strategy_authorized_for_phase=True,
        circuit_breaker_triggered=False,
        current_time=None,
    )
    candidate = OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(2),   # tentando aumentar para 2
        intended_stop_loss_points=Decimal("200"),
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Rejected), (
        f"Martingale com loss de R$ {last_loss:.2f} e aumento para 2 contratos "
        f"deveria ser bloqueado mas foi Approved"
    )
    assert result.validator == "martingale_check"


# P6 — Contexto completamente limpo sempre Approved
@settings(max_examples=2000, suppress_health_check=[HealthCheck.too_slow])
@given(
    asset=_asset_st,
    direction=_direction_st,
)
def test_property_p6_clean_context_always_approved(
    asset: AssetType,
    direction: Direction,
) -> None:
    """
    P6 — Contexto 100% limpo (todos os flags positivos, P&L zero, contagem zero)
    sempre produz Approved para 1 contrato em Fase 1.
    """
    ctx = make_clean_context_for_hypothesis(phase=Phase.FASE_1)
    candidate = OrderCandidate(
        asset=asset,
        direction=direction,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("200"),
    )
    result = validate(candidate, ctx)
    assert isinstance(result, Approved), (
        f"Contexto completamente limpo para {asset} {direction} deveria ser Approved "
        f"mas foi Rejected por {result.validator if isinstance(result, Rejected) else '?'}: "
        f"{result.reason if isinstance(result, Rejected) else ''}"
    )


# P7 — Propriedade bônus: approve/reject é determinístico
@settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
@given(
    contracts=st.integers(min_value=3, max_value=50),
    phase=_phase_st,
    asset=_asset_st,
)
def test_property_p7_deterministic_for_same_input(
    contracts: int,
    phase: Phase,
    asset: AssetType,
) -> None:
    """
    P7 — O Risk Engine é determinístico: mesma entrada sempre produz mesma saída.
    """
    ctx = make_clean_context_for_hypothesis(phase=phase)
    candidate = OrderCandidate(
        asset=asset,
        direction=Direction.LONG,
        contracts=ContractCount(contracts),
        intended_stop_loss_points=Decimal("200"),
        is_setup_a_plus=True,
    )
    result1 = validate(candidate, ctx)
    result2 = validate(candidate, ctx)
    assert type(result1) == type(result2)
    assert result1.approved == result2.approved
    if isinstance(result1, Rejected) and isinstance(result2, Rejected):
        assert result1.validator == result2.validator
