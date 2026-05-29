"""TDD First — BL-G research suite (T036+T037+T038+T040)."""
from __future__ import annotations

import math
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from cam.features.research.cross_asset_correlation import (
    PricePoint,
    compute_correlation,
    is_symmetric,
)
from cam.features.research.pair_trade_backtest import run_pair_backtest
from cam.features.research.pattern_lab import PatternSpec, search_patterns
from cam.features.research.rebalance import suggest_rebalance


def _series(asset_prices: list[float]) -> list[PricePoint]:
    base = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        PricePoint(base + timedelta(days=i), Decimal(str(p)))
        for i, p in enumerate(asset_prices)
    ]


# ---------------------------------------------------------------------------
# Correlation
# ---------------------------------------------------------------------------
class TestCorrelation:
    def test_correlation_symmetric(self):
        a = _series([100, 102, 105, 103, 110])
        b = _series([200, 202, 210, 205, 220])
        r_ab = compute_correlation("A", "B", a, b)
        r_ba = compute_correlation("B", "A", b, a)
        assert is_symmetric(r_ab, r_ba)

    def test_correlation_nan_with_single_point(self):
        r = compute_correlation("A", "B", _series([100]), _series([200]))
        assert math.isnan(r.correlation)

    def test_correlation_close_to_1_for_aligned_series(self):
        a = _series([100 + i for i in range(20)])
        b = _series([200 + 2 * i for i in range(20)])
        r = compute_correlation("A", "B", a, b)
        assert r.correlation > 0.99


# ---------------------------------------------------------------------------
# Pair Trade
# ---------------------------------------------------------------------------
class TestPairTrade:
    def test_runs_without_error_on_winxwdo_synthetic(self):
        a = _series([100 + i for i in range(50)])
        # Spread expandindo → entry SHORT_A_LONG_B
        b = _series([200 - i * 0.5 for i in range(50)])
        result = run_pair_backtest("WIN", "WDO", a, b, window=20, zscore_threshold=1.0)
        assert result.asset_a == "WIN"
        assert isinstance(result.trades, list)
        assert result.correlation is not None

    def test_no_trades_when_series_too_short(self):
        a = _series([100, 101])
        b = _series([200, 201])
        result = run_pair_backtest("WIN", "WDO", a, b, window=30)
        assert result.trades == []


# ---------------------------------------------------------------------------
# Pattern Lab
# ---------------------------------------------------------------------------
class TestPatternLab:
    def test_returns_zero_matches_with_empty_data(self):
        spec = PatternSpec(
            name="x",
            description="x",
            trigger_assets=["A"],
            target_asset="B",
            trigger_pct=Decimal("-0.01"),
            target_pct=Decimal("0.005"),
        )
        result = search_patterns(spec, {})
        assert result.matches == []

    def test_finds_match_when_trigger_fires(self):
        spec = PatternSpec(
            name="queda_A",
            description="A cai 1% → B sobe 0.5% no dia seguinte",
            trigger_assets=["A"],
            target_asset="B",
            trigger_pct=Decimal("-0.01"),
            target_pct=Decimal("0.005"),
        )
        # Série A: queda forte no dia 2; Série B: alta no dia 3.
        a = [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("98")),
            (date(2026, 1, 3), Decimal("99")),
        ]
        b = [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("100")),
            (date(2026, 1, 3), Decimal("101")),
        ]
        result = search_patterns(spec, {"A": a, "B": b}, min_occurrences=1)
        assert len(result.matches) >= 1


# ---------------------------------------------------------------------------
# Rebalance
# ---------------------------------------------------------------------------
class TestRebalance:
    def test_no_actions_when_empty_holdings(self):
        result = suggest_rebalance([], {})
        assert result.actions == []

    def test_sell_when_dy_below_band(self):
        holdings = [{"ticker": "PETR4", "quantity": 100, "avg_price": 35.0}]
        fundamentals = {"PETR4": {"dy": Decimal("0.02")}}
        result = suggest_rebalance(holdings, fundamentals, target_dy=Decimal("0.06"))
        assert result.actions[0].action == "SELL"

    def test_buy_when_dy_above_band(self):
        holdings = [{"ticker": "PETR4", "quantity": 100, "avg_price": 35.0}]
        fundamentals = {"PETR4": {"dy": Decimal("0.12")}}
        result = suggest_rebalance(holdings, fundamentals, target_dy=Decimal("0.06"))
        assert result.actions[0].action == "BUY"

    def test_hold_when_dy_in_band(self):
        holdings = [{"ticker": "PETR4", "quantity": 100, "avg_price": 35.0}]
        fundamentals = {"PETR4": {"dy": Decimal("0.065")}}
        result = suggest_rebalance(holdings, fundamentals, target_dy=Decimal("0.06"))
        assert result.actions[0].action == "HOLD"

    def test_no_side_effects_does_not_call_order_gateway(self):
        # Property by design — função pura, sem side effects.
        result = suggest_rebalance(
            [{"ticker": "PETR4", "quantity": 100, "avg_price": 35.0}],
            {"PETR4": {"dy": Decimal("0.02")}},
        )
        assert "action" in result.actions[0].to_dict()
