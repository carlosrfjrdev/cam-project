"""
TDD First — Autonomy Matrix (TASK-004 BL-A).

Cobertura:
- 16 combinações canônicas (4 envs × 4 modes) paramétricas.
- Casos especiais: RETIRED, REAL conditioned, DEMO conditioned, status mínimo.
"""
from __future__ import annotations

import pytest

from cam._shared.autonomy.matrix import (
    AutonomyContext,
    Env,
    Mode,
    is_mode_allowed,
)
from cam.features.strategies.domain import StrategyStatus

# ---------------------------------------------------------------------------
# Matriz canônica esperada (env, mode, status) -> bool
# Status REAL_AUTHORIZED (máximo) — para verificar "regras básicas" da matriz.
# ---------------------------------------------------------------------------
_MATRIX = {
    # Backtest: signal/semi/full ok; one_click N/A
    (Env.BACKTEST, Mode.SIGNAL): True,
    (Env.BACKTEST, Mode.ONE_CLICK): False,  # N/A
    (Env.BACKTEST, Mode.SEMI): True,
    (Env.BACKTEST, Mode.FULL): True,
    # Paper: tudo ok
    (Env.PAPER, Mode.SIGNAL): True,
    (Env.PAPER, Mode.ONE_CLICK): True,
    (Env.PAPER, Mode.SEMI): True,
    (Env.PAPER, Mode.FULL): True,
    # Demo: signal/one_click ok; semi/full cond. (cooldown_passed=True)
    (Env.DEMO, Mode.SIGNAL): True,
    (Env.DEMO, Mode.ONE_CLICK): True,
    (Env.DEMO, Mode.SEMI): True,
    (Env.DEMO, Mode.FULL): True,
    # Real: signal ok; one_click cond. forte; semi/full proibidos
    (Env.REAL, Mode.SIGNAL): True,
    (Env.REAL, Mode.ONE_CLICK): True,
    (Env.REAL, Mode.SEMI): False,
    (Env.REAL, Mode.FULL): False,
}


@pytest.mark.parametrize("env,mode,expected", [
    (env, mode, expected) for (env, mode), expected in _MATRIX.items()
])
def test_canonical_matrix_with_real_authorized_and_full_context(
    env: Env, mode: Mode, expected: bool
):
    """Status REAL_AUTHORIZED + contexto pleno cobre células condicionadas."""
    ctx = AutonomyContext(
        real_trading_allowed=True,
        cooldown_passed=True,
        signature_present=True,
    )
    decision = is_mode_allowed(env, mode, StrategyStatus.REAL_AUTHORIZED, ctx)
    assert decision.allowed is expected, decision.reason


# ---------------------------------------------------------------------------
# RETIRED bloqueia tudo
# ---------------------------------------------------------------------------
class TestRetiredBlocksAll:
    @pytest.mark.parametrize("env", list(Env))
    @pytest.mark.parametrize("mode", list(Mode))
    def test_retired_blocks_all_combinations(self, env, mode):
        ctx = AutonomyContext(
            real_trading_allowed=True,
            cooldown_passed=True,
            signature_present=True,
        )
        decision = is_mode_allowed(env, mode, StrategyStatus.RETIRED, ctx)
        assert decision.allowed is False


# ---------------------------------------------------------------------------
# REAL_TRADING_ALLOWED
# ---------------------------------------------------------------------------
class TestRealTradingAllowedGate:
    def test_real_blocked_when_real_trading_allowed_false(self):
        ctx = AutonomyContext(real_trading_allowed=False, cooldown_passed=True,
                              signature_present=True)
        d = is_mode_allowed(
            Env.REAL, Mode.SIGNAL, StrategyStatus.REAL_AUTHORIZED, ctx
        )
        assert d.allowed is False
        assert "REAL_TRADING_ALLOWED=false" in d.reason

    def test_real_signal_allowed_when_all_gates_passed(self):
        ctx = AutonomyContext(real_trading_allowed=True, cooldown_passed=True,
                              signature_present=True)
        d = is_mode_allowed(
            Env.REAL, Mode.SIGNAL, StrategyStatus.REAL_AUTHORIZED, ctx
        )
        assert d.allowed is True


# ---------------------------------------------------------------------------
# Status mínimo
# ---------------------------------------------------------------------------
class TestMinStatus:
    def test_paper_full_requires_backtested(self):
        d = is_mode_allowed(Env.PAPER, Mode.FULL, StrategyStatus.DRAFT)
        assert d.allowed is False
        assert "Status insuficiente" in d.reason

    def test_demo_full_requires_demo_ok(self):
        d = is_mode_allowed(Env.DEMO, Mode.FULL, StrategyStatus.PAPER_OK,
                            AutonomyContext(cooldown_passed=True))
        assert d.allowed is False
        assert "Status insuficiente" in d.reason

    def test_demo_one_click_with_paper_ok_allowed(self):
        d = is_mode_allowed(Env.DEMO, Mode.ONE_CLICK,
                            StrategyStatus.PAPER_OK)
        assert d.allowed is True


# ---------------------------------------------------------------------------
# REAL ONE_CLICK condicionado forte
# ---------------------------------------------------------------------------
class TestRealOneClickConditioned:
    def test_real_one_click_blocked_without_cooldown(self):
        ctx = AutonomyContext(real_trading_allowed=True,
                              cooldown_passed=False, signature_present=True)
        d = is_mode_allowed(Env.REAL, Mode.ONE_CLICK,
                            StrategyStatus.REAL_AUTHORIZED, ctx)
        assert d.allowed is False
        assert "cooldown" in d.reason.lower()

    def test_real_one_click_blocked_without_signature(self):
        ctx = AutonomyContext(real_trading_allowed=True,
                              cooldown_passed=True, signature_present=False)
        d = is_mode_allowed(Env.REAL, Mode.ONE_CLICK,
                            StrategyStatus.REAL_AUTHORIZED, ctx)
        assert d.allowed is False
        assert "assinatura" in d.reason.lower()


# ---------------------------------------------------------------------------
# DEMO SEMI/FULL condicionado
# ---------------------------------------------------------------------------
class TestDemoSemiFullConditioned:
    def test_demo_semi_blocked_without_cooldown(self):
        d = is_mode_allowed(Env.DEMO, Mode.SEMI, StrategyStatus.DEMO_OK,
                            AutonomyContext(cooldown_passed=False))
        assert d.allowed is False
        assert "condicionado" in d.reason.lower()

    def test_demo_full_allowed_with_cooldown(self):
        d = is_mode_allowed(Env.DEMO, Mode.FULL, StrategyStatus.DEMO_OK,
                            AutonomyContext(cooldown_passed=True))
        assert d.allowed is True
