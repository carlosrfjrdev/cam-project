"""
TDD First — Order Gateway (TASK-006 BL-A) — SEC CRÍTICO.

Cobre:
- real_trading_allowed=False bloqueia env=real.
- autonomy_matrix bloqueia combinação inválida.
- idempotency_key duplicada → rejeitada.
- risk_validate Rejected → dispatch não ocorre (verificado via mock).
- Pipeline correto: paper → paper_dispatcher; demo/real → ea_dispatcher.
- Property-based: NUNCA dispatch sem Approved no Risk Engine.
"""
from __future__ import annotations

from datetime import time
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st

from cam._shared.autonomy.matrix import AutonomyContext, Env, Mode
from cam._shared.config import Settings
from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    Phase,
)
from cam._shared.order_gateway.gateway import (
    BridgeUnavailableError,
    OrderGateway,
    OrderResult,
)
from cam._shared.risk import OrderCandidate, RiskContext
from cam.features.strategies.domain import StrategyStatus


# ---------------------------------------------------------------------------
# Fixtures de teste — Risk Context "limpo" (todas defesas em verde)
# ---------------------------------------------------------------------------
def _green_risk_context() -> RiskContext:
    """RiskContext em estado totalmente válido (todas defesas em verde)."""
    return RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000")),
        daily_pnl=Money.zero(),
        weekly_pnl=Money.zero(),
        monthly_pnl=Money.zero(),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
        strategy_authorized_for_phase=True,
        circuit_breaker_triggered=False,
        current_time=time(11, 30),  # janela de pregão WIN
    )


def _candidate() -> OrderCandidate:
    return OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("150"),
        is_setup_a_plus=True,
    )


def _settings(real_allowed: bool = False) -> Settings:
    accounts = ["12345"] if real_allowed else []
    return Settings(
        _env_file=None,
        real_trading_allowed=real_allowed,
        real_trading_accounts=accounts,
    )


# ---------------------------------------------------------------------------
# Dispatchers de teste
# ---------------------------------------------------------------------------
class _SpyPaper:
    def __init__(self) -> None:
        self.calls: list[tuple[OrderCandidate, UUID]] = []

    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]:
        self.calls.append((candidate, idempotency_key))
        return {"status": "spy_paper_ok"}


class _SpyEA:
    def __init__(self) -> None:
        self.calls: list[tuple[OrderCandidate, UUID]] = []

    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]:
        self.calls.append((candidate, idempotency_key))
        return {"status": "spy_ea_ok"}


# ---------------------------------------------------------------------------
# Casos básicos
# ---------------------------------------------------------------------------
class TestRealTradingGate:
    async def test_env_real_blocked_when_flag_false(self):
        gateway = OrderGateway(settings=_settings(real_allowed=False))
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.REAL,
            mode=Mode.SIGNAL,
            strategy_status=StrategyStatus.REAL_AUTHORIZED,
            idempotency_key=uuid4(),
        )
        assert result.approved is False
        assert result.validator == "real_trading_flag"


class TestAutonomyGate:
    async def test_autonomy_blocks_real_full(self):
        gateway = OrderGateway(settings=_settings(real_allowed=True))
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.REAL,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.REAL_AUTHORIZED,
            idempotency_key=uuid4(),
            autonomy_context=AutonomyContext(
                real_trading_allowed=True,
                cooldown_passed=True,
                signature_present=True,
            ),
        )
        assert result.approved is False
        assert result.validator == "autonomy_matrix"

    async def test_autonomy_blocks_paper_full_for_draft(self):
        gateway = OrderGateway(settings=_settings())
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.PAPER,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.DRAFT,
            idempotency_key=uuid4(),
        )
        assert result.approved is False
        assert result.validator == "autonomy_matrix"


class TestIdempotencyGate:
    async def test_duplicate_idempotency_key_rejected(self):
        gateway = OrderGateway(settings=_settings(), paper=_SpyPaper())
        key = uuid4()
        r1 = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.PAPER,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.BACKTESTED,
            idempotency_key=key,
        )
        r2 = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.PAPER,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.BACKTESTED,
            idempotency_key=key,
        )
        assert r1.approved is True
        assert r2.approved is False
        assert r2.validator == "idempotency"


class TestRiskEngineGate:
    async def test_kill_switch_active_blocks(self):
        gateway = OrderGateway(settings=_settings(), paper=_SpyPaper())
        rctx = _green_risk_context()
        # Forçar kill switch ativo via dataclass replace pattern
        rctx_killed = RiskContext(
            kill_switch_active=True,
            phase=rctx.phase,
            pre_market_checklist_done=rctx.pre_market_checklist_done,
            post_market_checklist_done=rctx.post_market_checklist_done,
            tax_compliance_ok=rctx.tax_compliance_ok,
            total_capital=rctx.total_capital,
            daily_pnl=rctx.daily_pnl,
            weekly_pnl=rctx.weekly_pnl,
            monthly_pnl=rctx.monthly_pnl,
            daily_operations_count=rctx.daily_operations_count,
            last_operation_result=rctx.last_operation_result,
            last_operation_contracts=rctx.last_operation_contracts,
            open_positions=rctx.open_positions,
            strategy_authorized_for_phase=rctx.strategy_authorized_for_phase,
            circuit_breaker_triggered=rctx.circuit_breaker_triggered,
            current_time=rctx.current_time,
        )
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=rctx_killed,
            env=Env.PAPER,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.BACKTESTED,
            idempotency_key=uuid4(),
        )
        assert result.approved is False
        # Risk engine assina como validator culpado
        assert result.validator is not None
        assert "kill_switch" in (result.validator or "")


class TestDispatchSelection:
    async def test_paper_env_routes_to_paper_dispatcher(self):
        paper = _SpyPaper()
        ea = _SpyEA()
        gateway = OrderGateway(settings=_settings(), paper=paper, ea=ea)
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.PAPER,
            mode=Mode.FULL,
            strategy_status=StrategyStatus.BACKTESTED,
            idempotency_key=uuid4(),
        )
        assert result.approved is True
        assert len(paper.calls) == 1
        assert len(ea.calls) == 0

    async def test_demo_env_routes_to_ea_dispatcher(self):
        paper = _SpyPaper()
        ea = _SpyEA()
        gateway = OrderGateway(settings=_settings(), paper=paper, ea=ea)
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.DEMO,
            mode=Mode.ONE_CLICK,
            strategy_status=StrategyStatus.PAPER_OK,
            idempotency_key=uuid4(),
        )
        assert result.approved is True
        assert len(ea.calls) == 1
        assert len(paper.calls) == 0

    async def test_ea_unavailable_returns_rejected(self):
        # default EA é _NullEADispatcher que levanta BridgeUnavailableError
        gateway = OrderGateway(settings=_settings())
        result = await gateway.submit(
            candidate=_candidate(),
            risk_context=_green_risk_context(),
            env=Env.DEMO,
            mode=Mode.ONE_CLICK,
            strategy_status=StrategyStatus.PAPER_OK,
            idempotency_key=uuid4(),
        )
        assert result.approved is False
        assert result.validator == "dispatcher"


# ---------------------------------------------------------------------------
# Property-based: invariante crítica.
# Para QUALQUER combinação de RiskContext, se OrderResult.approved == False,
# o EA dispatcher NUNCA pode ter sido invocado naquela chamada. E vice-versa:
# se approved == True, EA dispatcher foi invocado exatamente 1 vez.
# ---------------------------------------------------------------------------
@hyp_settings(max_examples=100, deadline=None)
@given(
    kill_switch=st.booleans(),
    pre_market=st.booleans(),
    post_market=st.booleans(),
    tax_ok=st.booleans(),
    daily_pnl_pct=st.floats(min_value=-0.05, max_value=0.05, allow_nan=False),
    daily_ops=st.integers(min_value=0, max_value=10),
    contracts=st.integers(min_value=1, max_value=5),
)
async def test_property_dispatch_count_matches_approval(
    kill_switch: bool,
    pre_market: bool,
    post_market: bool,
    tax_ok: bool,
    daily_pnl_pct: float,
    daily_ops: int,
    contracts: int,
):
    """
    Invariante: número de chamadas ao EA é exatamente 1 sse approved=True;
    é 0 sse approved=False. Equivale a "dispatch nunca ocorre sem aprovação".
    """
    pnl_amount = Decimal(str(daily_pnl_pct)) * Decimal("5000")
    rctx = RiskContext(
        kill_switch_active=kill_switch,
        phase=Phase.FASE_1,
        pre_market_checklist_done=pre_market,
        post_market_checklist_done=post_market,
        tax_compliance_ok=tax_ok,
        total_capital=Money(Decimal("5000")),
        daily_pnl=Money(pnl_amount),
        weekly_pnl=Money.zero(),
        monthly_pnl=Money.zero(),
        daily_operations_count=daily_ops,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
        strategy_authorized_for_phase=True,
        circuit_breaker_triggered=False,
        current_time=time(11, 30),
    )
    cand = OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(contracts),
        intended_stop_loss_points=Decimal("150"),
        is_setup_a_plus=True,
    )
    ea_spy = _SpyEA()
    gateway = OrderGateway(
        settings=_settings(real_allowed=True),
        ea=ea_spy,
    )
    result = await gateway.submit(
        candidate=cand,
        risk_context=rctx,
        env=Env.DEMO,
        mode=Mode.ONE_CLICK,
        strategy_status=StrategyStatus.PAPER_OK,
        idempotency_key=uuid4(),
    )
    if result.approved:
        assert len(ea_spy.calls) == 1
    else:
        assert len(ea_spy.calls) == 0
