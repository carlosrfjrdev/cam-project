"""TDD First — BL-F Policy Engine + Multi-Source Collector."""
from __future__ import annotations

import os
import subprocess
from datetime import UTC
from decimal import Decimal
from pathlib import Path

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam.features.fundamentals.multi_source_collector import (
    FundamentalsCollector,
    FundamentalsSnapshot,
    PlaceholderSource,
)
from cam.features.ledger.policy_engine import (
    PolicyAlert,
    evaluate_holding,
    is_blocking,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Policy Engine — unit
# ---------------------------------------------------------------------------
class TestPolicyEngine:
    def test_no_fundamentals_returns_nivel_1_alert(self):
        alerts = evaluate_holding({"ticker": "X"}, None)
        assert len(alerts) == 1
        assert alerts[0].code == "NO_FUNDAMENTALS"

    def test_dy_low_triggers_alert_1(self):
        alerts = evaluate_holding(
            {"ticker": "X"},
            {"dy": Decimal("0.02"), "pl": Decimal("10"),
             "div_liq_ebitda": Decimal("1.0")},
        )
        codes = {a.code for a in alerts}
        assert "DY_LOW" in codes

    def test_high_pl_triggers_alert_2(self):
        alerts = evaluate_holding(
            {"ticker": "X"},
            {"dy": Decimal("0.06"), "pl": Decimal("40"),
             "div_liq_ebitda": Decimal("1.0")},
        )
        codes = {a.code for a in alerts}
        assert "VALUATION_HIGH" in codes

    def test_high_leverage_triggers_alert_3(self):
        alerts = evaluate_holding(
            {"ticker": "X"},
            {"dy": Decimal("0.06"), "pl": Decimal("10"),
             "div_liq_ebitda": Decimal("5.0")},
        )
        codes = {a.code for a in alerts}
        assert "LEVERAGE_HIGH" in codes

    def test_no_alerts_when_in_thresholds(self):
        alerts = evaluate_holding(
            {"ticker": "X"},
            {"dy": Decimal("0.06"), "pl": Decimal("10"),
             "div_liq_ebitda": Decimal("1.0")},
        )
        assert alerts == []

    def test_is_blocking_always_false(self):
        alerts = [
            PolicyAlert(3, "X", "Y", "Z"),
            PolicyAlert(2, "A", "B", "C"),
        ]
        assert is_blocking(alerts) is False


# ---------------------------------------------------------------------------
# Multi-Source Collector — unit (sem DB)
# ---------------------------------------------------------------------------
class TestPlaceholderSource:
    @pytest.mark.asyncio
    async def test_returns_snapshot_for_PETR4(self):
        src = PlaceholderSource()
        snap = await src.fetch("PETR4")
        assert snap is not None
        assert snap.ticker == "PETR4"
        assert snap.dy == Decimal("0.0850")

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_ticker(self):
        src = PlaceholderSource()
        assert await src.fetch("UNKNOWN") is None


# ---------------------------------------------------------------------------
# Persistência DB
# ---------------------------------------------------------------------------
pytestmark_db = pytest.mark.skipif(
    not DB_AVAILABLE, reason="Requer DATABASE_URL"
)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _ensure_migrations_up():
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_ROOT),
        env={**os.environ, "DATABASE_URL": _DB_URL},
    )
    assert result.returncode == 0
    yield


@pytest_asyncio.fixture
async def clean_fundamentals():
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_fundamentals_snapshot"))
    yield


@pytestmark_db
async def test_collect_persists_snapshot(clean_fundamentals):
    collector = FundamentalsCollector()
    async with async_session_factory() as session:
        snap = await collector.collect(session, "PETR4")
    assert snap is not None
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        result = await conn.execute(
            _text(
                "SELECT COUNT(*) FROM cam_fundamentals_snapshot "
                "WHERE ticker = 'PETR4'"
            )
        )
        count = result.scalar()
    assert count == 1


@pytestmark_db
async def test_collect_idempotent_on_same_hash(clean_fundamentals):
    """Reinjetar mesmo snapshot (mesmo timestamp) → 0 duplicados."""
    from datetime import datetime

    collector = FundamentalsCollector()
    fixed_ts = datetime(2026, 5, 27, 22, 0, tzinfo=UTC)

    snap = FundamentalsSnapshot(
        ticker="PETR4",
        source="test",
        ts_snapshot=fixed_ts,
        dy=Decimal("0.08"),
    )
    async with async_session_factory() as session:
        await collector._persist(session, snap)
    async with async_session_factory() as session:
        await collector._persist(session, snap)
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        result = await conn.execute(
            _text(
                "SELECT COUNT(*) FROM cam_fundamentals_snapshot "
                "WHERE ticker = 'PETR4'"
            )
        )
        count = result.scalar()
    assert count == 1
