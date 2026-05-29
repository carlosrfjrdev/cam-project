"""TDD First — BL-H1 (TASK-042..049)."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from hypothesis import given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from cam._shared.autonomy.matrix import Env, Mode
from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
)
from cam._shared.risk.aggregate import (
    AggregateCandidate,
    AggregateContext,
    aggregate_risk_check,
)
from cam._shared.risk.context import OrderCandidate
from cam._shared.risk.decision import Approved, Rejected
from cam._shared.risk.limits import (
    DEFAULT_MAX_WDO_CONTRACTS,
    DEFAULT_MAX_WIN_CONTRACTS,
    CurrentLimits,
    get_current_limits,
    set_current_limits,
)
from cam.features.robot_orchestrator.conflict_resolver import (
    ConflictReason,
    ResolverCandidate,
    resolve,
)
from cam.features.robot_orchestrator.domain import (
    AmbiguousPriorityError,
    Robot,
    StrategyAssignment,
)
from cam.features.robot_orchestrator.orchestrator import RobotOrchestrator
from cam.features.strategies.domain import (
    StrategyContext,
    StrategyMetadata,
)


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------
class TestRobotDomain:
    def test_robot_aggregates_strategies(self):
        sid1, sid2 = uuid4(), uuid4()
        robot = Robot(
            id=uuid4(),
            name="r1",
            env=Env.PAPER,
            mode=Mode.FULL,
            strategies=(
                StrategyAssignment(strategy_id=sid1, priority=1),
                StrategyAssignment(strategy_id=sid2, priority=2),
            ),
        )
        assert len(robot.strategies) == 2

    def test_robot_zero_strategies_raises(self):
        with pytest.raises(ValueError):
            Robot(
                id=uuid4(),
                name="r1",
                env=Env.PAPER,
                mode=Mode.FULL,
                strategies=(),
            )

    def test_priority_duplicates_raises(self):
        with pytest.raises(AmbiguousPriorityError):
            Robot(
                id=uuid4(),
                name="r1",
                env=Env.PAPER,
                mode=Mode.FULL,
                strategies=(
                    StrategyAssignment(uuid4(), 1),
                    StrategyAssignment(uuid4(), 1),
                ),
            )


# ---------------------------------------------------------------------------
# Conflict Resolver
# ---------------------------------------------------------------------------
def _cand(direction=Direction.LONG, expectancy="100", asset=AssetType.WIN,
          suspended=False) -> ResolverCandidate:
    return ResolverCandidate(
        strategy_id=uuid4(),
        asset=asset,
        direction=direction,
        contracts=1,
        expectancy_30d=Decimal(str(expectancy)),
        is_suspended=suspended,
    )


class TestConflictResolver:
    def test_single_candidate_passes_through(self):
        c = _cand()
        r = resolve([c])
        assert r.winners == [c]
        assert r.rejected == []

    def test_directional_conflict_same_asset(self):
        a = _cand(direction=Direction.LONG)
        b = _cand(direction=Direction.SHORT)
        r = resolve([a, b])
        assert r.winners == []
        assert len(r.rejected) == 2
        codes = {audit[1] for audit in r.audits}
        assert ConflictReason.DIRECTIONAL_CONFLICT.value in codes

    def test_same_direction_higher_expectancy_wins(self):
        a = _cand(expectancy="200")
        b = _cand(expectancy="100")
        r = resolve([a, b])
        assert r.winners == [a]
        assert b in r.rejected

    def test_ambiguous_tie_within_5pct(self):
        a = _cand(expectancy="100")
        b = _cand(expectancy="101")  # < 5% diff
        r = resolve([a, b])
        assert r.winners == []
        codes = {audit[1] for audit in r.audits}
        assert ConflictReason.AMBIGUOUS_TIE.value in codes

    def test_different_assets_both_pass(self):
        a = _cand(asset=AssetType.WIN)
        b = _cand(asset=AssetType.WDO)
        r = resolve([a, b])
        assert set(r.winners) == {a, b}

    def test_suspended_skipped(self):
        a = _cand(suspended=True)
        b = _cand()
        r = resolve([a, b])
        assert b in r.winners
        assert a in r.rejected


# ---------------------------------------------------------------------------
# Aggregate Risk Check
# ---------------------------------------------------------------------------
class TestAggregateRisk:
    def setup_method(self) -> None:
        # Reset override antes de cada teste
        set_current_limits(None)

    def test_default_limits_accept_2_win(self):
        c = AggregateCandidate("s1", AssetType.WIN, 2, Decimal("0.98"))
        result = aggregate_risk_check([c], AggregateContext())
        assert isinstance(result, Approved)

    def test_default_limits_reject_3_win(self):
        c1 = AggregateCandidate("s1", AssetType.WIN, 2, Decimal("0.98"))
        c2 = AggregateCandidate("s2", AssetType.WIN, 1, Decimal("0.98"))
        result = aggregate_risk_check([c1, c2], AggregateContext())
        assert isinstance(result, Rejected)
        assert "max_win" in result.validator

    def test_adherence_below_95_rejects(self):
        c = AggregateCandidate("s1", AssetType.WIN, 1, Decimal("0.94"))
        result = aggregate_risk_check(
            [c],
            AggregateContext(strategy_adherence={"s1": Decimal("0.94")}),
        )
        assert isinstance(result, Rejected)
        assert "adherence" in result.validator

    def test_correlation_above_0_7_rejects(self):
        c1 = AggregateCandidate("s1", AssetType.WIN, 1, Decimal("0.98"))
        c2 = AggregateCandidate("s2", AssetType.WDO, 1, Decimal("0.98"))
        result = aggregate_risk_check(
            [c1, c2],
            AggregateContext(correlations={("s1", "s2"): 0.85}),
        )
        assert isinstance(result, Rejected)
        assert "correlation" in result.validator

    def test_scaled_limits_accept_3_win(self):
        set_current_limits(CurrentLimits(
            max_win=5, max_wdo=5,
            max_daily_drawdown_pct=Decimal("0.03"),
            is_scaled=True, source="test_override",
        ))
        c1 = AggregateCandidate("s1", AssetType.WIN, 3, Decimal("0.98"))
        result = aggregate_risk_check([c1], AggregateContext())
        assert isinstance(result, Approved)
        set_current_limits(None)

    @hyp_settings(max_examples=200, deadline=None)
    @given(
        win_open=st.integers(min_value=0, max_value=3),
        wdo_open=st.integers(min_value=0, max_value=3),
        win_new=st.integers(min_value=0, max_value=3),
        wdo_new=st.integers(min_value=0, max_value=3),
    )
    def test_property_never_approves_above_default_limit(
        self, win_open, wdo_open, win_new, wdo_new,
    ):
        """Para qualquer combinação, aprovação implica soma ≤ limite vigente."""
        set_current_limits(None)
        candidates = []
        if win_new > 0:
            candidates.append(
                AggregateCandidate("s1", AssetType.WIN, win_new, Decimal("0.98"))
            )
        if wdo_new > 0:
            candidates.append(
                AggregateCandidate("s2", AssetType.WDO, wdo_new, Decimal("0.98"))
            )
        if not candidates:
            return
        result = aggregate_risk_check(
            candidates,
            AggregateContext(
                open_win_contracts=win_open,
                open_wdo_contracts=wdo_open,
            ),
        )
        if isinstance(result, Approved):
            assert win_open + win_new <= DEFAULT_MAX_WIN_CONTRACTS
            assert wdo_open + wdo_new <= DEFAULT_MAX_WDO_CONTRACTS


# ---------------------------------------------------------------------------
# Current Limits
# ---------------------------------------------------------------------------
class TestCurrentLimits:
    def test_default_is_2_2(self):
        set_current_limits(None)
        cur = get_current_limits()
        assert cur.max_win == 2
        assert cur.max_wdo == 2
        assert cur.is_scaled is False

    def test_override_via_set(self):
        set_current_limits(CurrentLimits(
            max_win=4, max_wdo=4,
            max_daily_drawdown_pct=Decimal("0.03"),
            is_scaled=True, source="scaling_event:abc",
        ))
        cur = get_current_limits()
        assert cur.max_win == 4
        assert cur.is_scaled is True
        set_current_limits(None)


# ---------------------------------------------------------------------------
# Orchestrator (smoke)
# ---------------------------------------------------------------------------
class _DummyStrategy:
    def __init__(self, sid: UUID, returns_candidate: bool = True):
        self.metadata = StrategyMetadata(
            id=sid,
            name="dummy",
            version="0.0.1",
            asset=AssetType.WIN,
            author="test",
        )
        self._returns = returns_candidate

    def evaluate(self, tick, ctx):
        if not self._returns:
            return None
        return OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("150"),
        )


class TestOrchestrator:
    def test_orchestrator_handles_single_strategy_default(self):
        sid = uuid4()
        robot = Robot(
            id=uuid4(),
            name="r1",
            env=Env.PAPER,
            mode=Mode.FULL,
            strategies=(StrategyAssignment(sid, 1),),
        )
        orch = RobotOrchestrator(
            robot=robot,
            strategy_runtime={str(sid): _DummyStrategy(sid)},
            expectancy_lookup={str(sid): Decimal("100")},
            suspended_lookup={},
        )
        result = orch.handle_tick({"price": 130000}, StrategyContext(tick={}))
        assert result.candidates_emitted == 1
        assert len(result.winners) == 1

    def test_orchestrator_skips_suspended(self):
        sid = uuid4()
        robot = Robot(
            id=uuid4(),
            name="r1",
            env=Env.PAPER,
            mode=Mode.FULL,
            strategies=(StrategyAssignment(sid, 1),),
        )
        orch = RobotOrchestrator(
            robot=robot,
            strategy_runtime={str(sid): _DummyStrategy(sid)},
            expectancy_lookup={str(sid): Decimal("100")},
            suspended_lookup={str(sid): True},
        )
        result = orch.handle_tick({"price": 130000}, StrategyContext(tick={}))
        assert result.candidates_emitted == 0
