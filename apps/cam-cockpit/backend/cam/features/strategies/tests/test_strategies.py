"""
TDD First — testes do domínio de estratégias (TASK-001 BL-A).

Cobre:
- StrategyStatus: enum com 7 estados monotônicos.
- is_valid_transition: regras de transição (monotônica + qualquer → retired).
- StrategyMetadata: dataclass frozen com campos obrigatórios.
- Strategy Protocol: contrato evaluate(tick, context) -> OrderCandidate | None.
- StrategyContext: snapshot entregue ao evaluate.
"""
from decimal import Decimal
from uuid import uuid4

import pytest

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
)
from cam._shared.risk.context import OrderCandidate
from cam.features.strategies.domain import (
    Strategy,
    StrategyContext,
    StrategyMetadata,
    StrategyStatus,
    is_valid_transition,
)


# ---------------------------------------------------------------------------
# StrategyStatus
# ---------------------------------------------------------------------------
class TestStrategyStatus:
    def test_enum_has_exactly_seven_values(self):
        assert len(list(StrategyStatus)) == 7

    def test_enum_values_exact(self):
        # ordem importa para promoções monotônicas
        expected = [
            "draft",
            "backtested",
            "walk_forward_ok",
            "paper_ok",
            "demo_ok",
            "real_authorized",
            "retired",
        ]
        assert [s.value for s in StrategyStatus] == expected


# ---------------------------------------------------------------------------
# is_valid_transition
# ---------------------------------------------------------------------------
class TestStatusTransition:
    def test_forward_transition_allowed(self):
        assert is_valid_transition(
            StrategyStatus.PAPER_OK, StrategyStatus.DEMO_OK
        )

    def test_backward_transition_rejected(self):
        assert not is_valid_transition(
            StrategyStatus.PAPER_OK, StrategyStatus.BACKTESTED
        )

    def test_skipping_status_rejected(self):
        # draft → demo_ok exige passar por backtested + walk_forward_ok + paper_ok
        assert not is_valid_transition(
            StrategyStatus.DRAFT, StrategyStatus.DEMO_OK
        )

    def test_any_to_retired_allowed(self):
        for src in StrategyStatus:
            if src is StrategyStatus.RETIRED:
                continue
            assert is_valid_transition(src, StrategyStatus.RETIRED), src

    def test_retired_is_terminal(self):
        # após retired, não pode reativar (decisão constitucional — retire é sticky)
        assert not is_valid_transition(
            StrategyStatus.RETIRED, StrategyStatus.PAPER_OK
        )

    def test_same_status_is_not_a_transition(self):
        assert not is_valid_transition(
            StrategyStatus.PAPER_OK, StrategyStatus.PAPER_OK
        )

    def test_only_consecutive_forward_step_allowed(self):
        assert is_valid_transition(
            StrategyStatus.DRAFT, StrategyStatus.BACKTESTED
        )
        # pular 1 ainda é proibido
        assert not is_valid_transition(
            StrategyStatus.DRAFT, StrategyStatus.WALK_FORWARD_OK
        )


# ---------------------------------------------------------------------------
# StrategyMetadata
# ---------------------------------------------------------------------------
class TestStrategyMetadata:
    def test_metadata_required_fields_present(self):
        m = StrategyMetadata(
            id=uuid4(),
            name="S1 ORB",
            version="1.0.0",
            asset=AssetType.WIN,
            author="Carlos",
        )
        assert m.name == "S1 ORB"
        assert m.version == "1.0.0"
        assert m.asset is AssetType.WIN
        assert m.custom_metrics == {}

    def test_metadata_is_frozen(self):
        from dataclasses import FrozenInstanceError

        m = StrategyMetadata(
            id=uuid4(),
            name="S1 ORB",
            version="1.0.0",
            asset=AssetType.WIN,
            author="Carlos",
        )
        with pytest.raises(FrozenInstanceError):
            m.name = "OUTRA"  # type: ignore[misc]

    def test_metadata_accepts_custom_metrics(self):
        m = StrategyMetadata(
            id=uuid4(),
            name="S1 ORB",
            version="1.0.0",
            asset=AssetType.WIN,
            author="Carlos",
            custom_metrics={"opening_range_minutes": 60},
        )
        assert m.custom_metrics["opening_range_minutes"] == 60


# ---------------------------------------------------------------------------
# StrategyContext
# ---------------------------------------------------------------------------
class TestStrategyContext:
    def test_context_default_max_contracts_is_2(self):
        ctx = StrategyContext(tick={"price": 130000})
        assert ctx.max_contracts == 2

    def test_context_history_defaults_to_empty(self):
        ctx = StrategyContext(tick={"price": 130000})
        assert ctx.history == []

    def test_context_flags_defaults_to_empty(self):
        ctx = StrategyContext(tick={"price": 130000})
        assert ctx.flags == {}


# ---------------------------------------------------------------------------
# Strategy Protocol
# ---------------------------------------------------------------------------
class _DummyStrategyNone:
    """Implementação dummy que sempre retorna None."""

    def __init__(self):
        self.metadata = StrategyMetadata(
            id=uuid4(),
            name="dummy",
            version="0.0.1",
            asset=AssetType.WIN,
            author="test",
        )

    def evaluate(self, tick, context):
        return None


class _DummyStrategyAlwaysLong:
    """Implementação dummy que sempre retorna OrderCandidate LONG."""

    def __init__(self):
        self.metadata = StrategyMetadata(
            id=uuid4(),
            name="dummy_long",
            version="0.0.1",
            asset=AssetType.WIN,
            author="test",
        )

    def evaluate(self, tick, context):
        return OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(1),
            intended_stop_loss_points=Decimal("150"),
        )


class TestStrategyProtocol:
    def test_dummy_none_satisfies_protocol(self):
        s = _DummyStrategyNone()
        assert isinstance(s, Strategy)

    def test_dummy_long_satisfies_protocol(self):
        s = _DummyStrategyAlwaysLong()
        assert isinstance(s, Strategy)

    def test_evaluate_returning_none_is_valid(self):
        s = _DummyStrategyNone()
        result = s.evaluate({"price": 130000}, StrategyContext(tick={"price": 130000}))
        assert result is None

    def test_evaluate_returning_candidate_has_correct_type(self):
        s = _DummyStrategyAlwaysLong()
        result = s.evaluate(
            {"price": 130000}, StrategyContext(tick={"price": 130000})
        )
        assert isinstance(result, OrderCandidate)
        assert result.direction is Direction.LONG
