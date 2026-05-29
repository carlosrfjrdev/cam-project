"""
T-B04 — Validators Grupo 3: Limites de P&L (posições 9–12).

Validators testados:
    9.  daily_loss_limit_check   (Art. 16º — 3% do capital)
    10. weekly_loss_limit_check  (Art. 16º — 7% do capital)
    11. monthly_loss_limit_check (Art. 16º — 15% do capital)
    12. gain_lock_check          (Art. 17º — 2% do capital)

Todos os limites são calculados como percentual do total_capital.
Sobre capital de R$ 5.000:
    Limite diário de loss:   3% = R$ 150,00
    Limite semanal de loss:  7% = R$ 350,00
    Limite mensal de loss:  15% = R$ 750,00
    Gain lock:               2% = R$ 100,00
"""
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import AssetType, ContractCount, Direction, Money, Phase
from cam._shared.risk import Approved, OrderCandidate, Rejected, RiskContext, validate

CAPITAL = Decimal("5000.00")


def make_base_context(**overrides) -> RiskContext:
    """Contexto limpo com capital padrão de R$ 5.000."""
    defaults: dict = dict(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(CAPITAL),
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


class TestDailyLossLimitCheck:
    """Validator 9 — Art. 16º: 3% do capital total bloqueia o dia."""

    def test_daily_loss_at_exactly_3pct_rejects(self):
        """P&L diário = exatamente -3% → Rejected."""
        ctx = make_base_context(
            total_capital=Money(CAPITAL),
            daily_pnl=Money(Decimal("-150.00")),  # 3% de 5000
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_loss_limit_check"

    def test_daily_loss_above_3pct_rejects(self):
        """P&L diário = -5% → Rejected."""
        ctx = make_base_context(daily_pnl=Money(Decimal("-250.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_loss_limit_check"

    def test_daily_loss_at_2pct_passes(self):
        """P&L diário = -2% → NÃO bloqueado por daily_loss_limit_check."""
        ctx = make_base_context(daily_pnl=Money(Decimal("-100.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_loss_limit_check"

    def test_daily_loss_at_2_99pct_passes(self):
        """P&L diário = -R$ 149,99 (< 3%) → NÃO bloqueado."""
        ctx = make_base_context(daily_pnl=Money(Decimal("-149.99")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_loss_limit_check"

    def test_daily_pnl_zero_passes(self):
        """P&L diário = R$ 0,00 → NÃO bloqueado."""
        ctx = make_base_context(daily_pnl=Money(Decimal("0.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_loss_limit_check"

    def test_daily_pnl_positive_not_blocked_by_loss_check(self):
        """P&L positivo não é bloqueado por daily_loss_limit_check."""
        ctx = make_base_context(daily_pnl=Money(Decimal("50.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_loss_limit_check"

    def test_daily_loss_reason_mentions_art16_or_limite(self):
        ctx = make_base_context(daily_pnl=Money(Decimal("-150.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        reason_lower = result.reason.lower()
        assert "16" in result.reason or "limite" in reason_lower or "diário" in reason_lower

    def test_daily_loss_limit_scales_with_capital(self):
        """O limite é percentual — escala com o capital declarado."""
        # Capital de R$ 10.000 → limite diário = R$ 300,00
        ctx = make_base_context(
            total_capital=Money(Decimal("10000.00")),
            daily_pnl=Money(Decimal("-300.00")),  # 3% de 10000
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_loss_limit_check"

    def test_daily_loss_below_scaled_limit_passes(self):
        """Com capital de R$ 10.000, -R$ 299,99 não bloqueia."""
        ctx = make_base_context(
            total_capital=Money(Decimal("10000.00")),
            daily_pnl=Money(Decimal("-299.99")),
        )
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "daily_loss_limit_check"


class TestWeeklyLossLimitCheck:
    """Validator 10 — Art. 16º: 7% do capital total bloqueia a semana."""

    def test_weekly_loss_at_exactly_7pct_rejects(self):
        """P&L semanal = -7% = -R$ 350,00 → Rejected."""
        ctx = make_base_context(weekly_pnl=Money(Decimal("-350.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "weekly_loss_limit_check"

    def test_weekly_loss_above_7pct_rejects(self):
        ctx = make_base_context(weekly_pnl=Money(Decimal("-400.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "weekly_loss_limit_check"

    def test_weekly_loss_below_7pct_passes(self):
        """P&L semanal = -R$ 349,99 → NÃO bloqueado por weekly_loss_limit_check."""
        ctx = make_base_context(weekly_pnl=Money(Decimal("-349.99")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "weekly_loss_limit_check"

    def test_weekly_loss_zero_passes(self):
        ctx = make_base_context(weekly_pnl=Money(Decimal("0.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "weekly_loss_limit_check"

    def test_weekly_loss_scales_with_capital(self):
        ctx = make_base_context(
            total_capital=Money(Decimal("10000.00")),
            weekly_pnl=Money(Decimal("-700.00")),  # 7% de 10000
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "weekly_loss_limit_check"


class TestMonthlyLossLimitCheck:
    """Validator 11 — Art. 16º: 15% do capital total congela a fase."""

    def test_monthly_loss_at_exactly_15pct_rejects(self):
        """P&L mensal = -15% = -R$ 750,00 → Rejected."""
        ctx = make_base_context(monthly_pnl=Money(Decimal("-750.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "monthly_loss_limit_check"

    def test_monthly_loss_above_15pct_rejects(self):
        ctx = make_base_context(monthly_pnl=Money(Decimal("-800.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "monthly_loss_limit_check"

    def test_monthly_loss_below_15pct_passes(self):
        """P&L mensal = -R$ 749,99 → NÃO bloqueado por monthly_loss_limit_check."""
        ctx = make_base_context(monthly_pnl=Money(Decimal("-749.99")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "monthly_loss_limit_check"

    def test_monthly_loss_reason_mentions_freeze_or_fase(self):
        """Motivo deve indicar que a fase é congelada."""
        ctx = make_base_context(monthly_pnl=Money(Decimal("-750.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        reason_lower = result.reason.lower()
        assert "congel" in reason_lower or "fase" in reason_lower or "15" in result.reason

    def test_monthly_loss_scales_with_capital(self):
        ctx = make_base_context(
            total_capital=Money(Decimal("10000.00")),
            monthly_pnl=Money(Decimal("-1500.00")),  # 15% de 10000
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "monthly_loss_limit_check"


class TestGainLockCheck:
    """Validator 12 — Art. 17º: 2% de ganho no dia encerra o pregão."""

    def test_gain_at_exactly_2pct_rejects(self):
        """P&L diário = +2% = +R$ 100,00 → Rejected (gain lock)."""
        ctx = make_base_context(daily_pnl=Money(Decimal("100.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "gain_lock_check"

    def test_gain_above_2pct_rejects(self):
        """P&L diário = +R$ 150,00 → Rejected."""
        ctx = make_base_context(daily_pnl=Money(Decimal("150.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "gain_lock_check"

    def test_gain_below_2pct_passes(self):
        """P&L diário = +R$ 99,99 (< 2%) → NÃO bloqueado por gain_lock_check."""
        ctx = make_base_context(daily_pnl=Money(Decimal("99.99")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "gain_lock_check"

    def test_gain_lock_zero_pnl_passes(self):
        """P&L zero não aciona gain lock."""
        ctx = make_base_context(daily_pnl=Money(Decimal("0.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "gain_lock_check"

    def test_gain_lock_negative_pnl_passes(self):
        """P&L negativo não aciona gain lock."""
        ctx = make_base_context(daily_pnl=Money(Decimal("-50.00")))
        result = validate(make_candidate(), ctx)
        if isinstance(result, Rejected):
            assert result.validator != "gain_lock_check"

    def test_gain_lock_reason_mentions_art17_or_gain(self):
        ctx = make_base_context(daily_pnl=Money(Decimal("100.00")))
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        reason_lower = result.reason.lower()
        assert "17" in result.reason or "gain" in reason_lower or "lucro" in reason_lower or "dia" in reason_lower

    def test_gain_lock_scales_with_capital(self):
        """Gain lock escala com o capital declarado."""
        ctx = make_base_context(
            total_capital=Money(Decimal("10000.00")),
            daily_pnl=Money(Decimal("200.00")),  # 2% de 10000
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "gain_lock_check"


class TestGroup3PrioritiesAndInteractions:
    """Testa prioridades dentro do Grupo 3 e interação com grupos anteriores."""

    def test_daily_loss_checked_before_weekly_loss(self):
        """
        daily_loss_limit_check (pos 9) tem prioridade sobre weekly_loss_limit_check (pos 10).
        Se ambos falham, o validator 9 vence.
        """
        ctx = make_base_context(
            daily_pnl=Money(Decimal("-150.00")),   # 3% — aciona diário
            weekly_pnl=Money(Decimal("-350.00")),  # 7% — aciona semanal também
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_loss_limit_check"

    def test_weekly_loss_checked_before_monthly_loss(self):
        ctx = make_base_context(
            daily_pnl=Money(Decimal("0.00")),
            weekly_pnl=Money(Decimal("-350.00")),   # 7%
            monthly_pnl=Money(Decimal("-750.00")),  # 15%
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "weekly_loss_limit_check"

    def test_monthly_loss_checked_before_gain_lock(self):
        """
        monthly_loss_limit_check (pos 11) antes de gain_lock_check (pos 12).
        Combinação improvável mas possível: mês com loss mas hoje com gain.
        """
        ctx = make_base_context(
            daily_pnl=Money(Decimal("100.00")),     # gain lock
            monthly_pnl=Money(Decimal("-750.00")),  # monthly loss
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "monthly_loss_limit_check"

    def test_gain_lock_does_not_interfere_with_loss_checks(self):
        """gain_lock_check só atua quando P&L é positivo."""
        ctx = make_base_context(
            daily_pnl=Money(Decimal("-150.00")),  # loss diário
        )
        result = validate(make_candidate(), ctx)
        assert isinstance(result, Rejected)
        assert result.validator == "daily_loss_limit_check"
        # Não deve ser gain_lock_check
        assert result.validator != "gain_lock_check"
