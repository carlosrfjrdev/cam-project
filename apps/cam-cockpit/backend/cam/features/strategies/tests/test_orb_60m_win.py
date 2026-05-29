"""
TDD First — S1 ORB 60m WIN (TASK-007 BL-A).
"""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from cam._shared.domain.primitives import AssetType, Direction
from cam._shared.risk.context import OrderCandidate
from cam.features.strategies.domain import Strategy, StrategyContext
from cam.features.strategies.strategies.orb_60m_win import ORB60mWIN


def _tick(ts: datetime, price, *, high=None, low=None) -> dict:
    return {
        "timestamp": ts,
        "price": Decimal(str(price)),
        "high": Decimal(str(high)) if high is not None else Decimal(str(price)),
        "low": Decimal(str(low)) if low is not None else Decimal(str(price)),
    }


class TestProtocolCompliance:
    def test_orb_satisfies_strategy_protocol(self):
        s = ORB60mWIN()
        assert isinstance(s, Strategy)

    def test_metadata_correct(self):
        s = ORB60mWIN()
        assert s.metadata.name == "S1 ORB 60m WIN"
        assert s.metadata.asset is AssetType.WIN
        assert s.metadata.version == "1.0.0"
        assert s.metadata.custom_metrics["opening_range_minutes"] == 60


class TestOpeningRangeWindow:
    def test_no_signal_during_opening_range(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)
        # Ticks entre 09h00 e 10h00 nunca disparam
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        for minute in range(0, 60, 5):
            ts = base.replace(minute=minute)
            assert s.evaluate(_tick(ts, 130000 + minute * 10), ctx) is None

    def test_no_signal_during_grace_window(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)
        # Constrói range
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        for minute in range(0, 60, 5):
            s.evaluate(_tick(base.replace(minute=minute), 130000), ctx)
        # Janela de folga 10h00–10h15 — nenhum sinal
        for minute in range(0, 15, 5):
            ts = datetime(2026, 5, 27, 10, minute, tzinfo=UTC)
            assert s.evaluate(_tick(ts, 131000), ctx) is None


class TestLongEntry:
    def test_long_entry_when_close_breaks_high(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)

        # Constrói range com high=130500, low=129500
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(base, 130000, high=130500, low=129500), ctx)
        s.evaluate(
            _tick(base.replace(minute=30), 130200, high=130400, low=129800),
            ctx,
        )

        # Tick depois das 10h15 com preço > OR_high
        ts_break = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        result = s.evaluate(_tick(ts_break, 130600), ctx)

        assert isinstance(result, OrderCandidate)
        assert result.direction is Direction.LONG
        assert result.asset is AssetType.WIN
        assert result.intended_stop_loss_points == Decimal("150")


class TestShortEntry:
    def test_short_entry_when_close_breaks_low(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)

        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(base, 130000, high=130500, low=129500), ctx)

        ts_break = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        result = s.evaluate(_tick(ts_break, 129000), ctx)

        assert isinstance(result, OrderCandidate)
        assert result.direction is Direction.SHORT


class TestMaxContractsRespected:
    def test_orb_never_proposes_more_than_2_contracts(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=10)  # tenta forçar
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(base, 130000, high=130500, low=129500), ctx)
        ts_break = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        result = s.evaluate(_tick(ts_break, 130600), ctx)
        assert result is not None
        # Art. 11º — cap em 2 mesmo se contexto pedir mais
        assert result.contracts.value == 2

    def test_orb_uses_max_contracts_when_below_2(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=1)
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(base, 130000, high=130500, low=129500), ctx)
        ts_break = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        result = s.evaluate(_tick(ts_break, 130600), ctx)
        assert result is not None
        assert result.contracts.value == 1


class TestSingleShotPerDirection:
    def test_long_arms_only_once_per_session(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)
        base = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(base, 130000, high=130500, low=129500), ctx)
        ts1 = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        ts2 = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
        first = s.evaluate(_tick(ts1, 130600), ctx)
        second = s.evaluate(_tick(ts2, 130800), ctx)
        assert first is not None
        assert second is None  # 1 shot por dia por direção


class TestSessionReset:
    def test_new_day_resets_arm_flags(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)
        day1_open = datetime(2026, 5, 27, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(day1_open, 130000, high=130500, low=129500), ctx)
        d1_trigger = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        s.evaluate(_tick(d1_trigger, 130600), ctx)  # consome long

        day2_open = datetime(2026, 5, 28, 9, 0, tzinfo=UTC)
        s.evaluate(_tick(day2_open, 131000, high=131500, low=130500), ctx)
        d2_trigger = datetime(2026, 5, 28, 10, 30, tzinfo=UTC)
        result = s.evaluate(_tick(d2_trigger, 131600), ctx)
        assert result is not None
        assert result.direction is Direction.LONG


class TestNoSignalWithoutRange:
    def test_no_signal_if_tick_arrives_after_or_window_without_range(self):
        s = ORB60mWIN()
        ctx = StrategyContext(tick={}, max_contracts=2)
        # Pula direto para 10h30 sem ticks no range
        ts = datetime(2026, 5, 27, 10, 30, tzinfo=UTC)
        result = s.evaluate(_tick(ts, 130000), ctx)
        assert result is None
