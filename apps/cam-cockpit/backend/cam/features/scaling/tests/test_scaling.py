"""TDD First — BL-H2 (T050..T057)."""
from __future__ import annotations

import os
import subprocess
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam._shared.risk.scaling import (
    COOLDOWN_DEFAULT_DAYS,
    COOLDOWN_WIN_STREAK_DAYS,
    EVALUATION_WINDOW_PREGOES,
    MAX_SCALED_WDO,
    MAX_SCALED_WIN,
    BlockedByCeilingError,
    IncrementalViolationError,
    ScalingEvidence,
    compute_cooldown_days,
    compute_scaling_eligibility,
    detect_win_streak,
    validate_incremental_step,
)
from cam.features.scaling.repository import ScalingEventsRepository

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Eligibility (unit)
# ---------------------------------------------------------------------------
def _good_evidence(**overrides) -> ScalingEvidence:
    base = dict(
        profit_factor=Decimal("2.0"),
        win_rate=Decimal("0.60"),
        expectancy_net=Decimal("3000"),
        monthly_fixed_cost=Decimal("1000"),  # → threshold 1500
        drawdown_pct=Decimal("0.08"),
        adherence=Decimal("0.96"),
        pregoes_count=EVALUATION_WINDOW_PREGOES,
        prev_period_was_scaled=False,
    )
    base.update(overrides)
    return ScalingEvidence(**base)


class TestEligibility:
    def test_eligible_when_all_5_criteria_met(self):
        result = compute_scaling_eligibility(_good_evidence())
        assert result.eligible is True
        assert result.missing_criteria == []

    def test_not_eligible_with_low_profit_factor(self):
        result = compute_scaling_eligibility(
            _good_evidence(profit_factor=Decimal("1.5"))
        )
        assert result.eligible is False
        assert any("profit_factor" in m for m in result.missing_criteria)

    def test_not_eligible_with_low_win_rate(self):
        result = compute_scaling_eligibility(
            _good_evidence(win_rate=Decimal("0.40"))
        )
        assert result.eligible is False
        assert any("win_rate" in m for m in result.missing_criteria)

    def test_not_eligible_with_low_expectancy(self):
        result = compute_scaling_eligibility(
            _good_evidence(expectancy_net=Decimal("1000"))
        )
        assert result.eligible is False
        assert any("expectancy_net" in m for m in result.missing_criteria)

    def test_not_eligible_with_high_drawdown(self):
        result = compute_scaling_eligibility(
            _good_evidence(drawdown_pct=Decimal("0.12"))
        )
        assert result.eligible is False
        assert any("drawdown" in m for m in result.missing_criteria)

    def test_not_eligible_with_low_adherence(self):
        result = compute_scaling_eligibility(
            _good_evidence(adherence=Decimal("0.90"))
        )
        assert result.eligible is False
        assert any("adherence" in m for m in result.missing_criteria)

    def test_drawdown_doubles_when_prev_scaled(self):
        """Voltaire 2: DD em dobro se período anterior foi escalonado."""
        result = compute_scaling_eligibility(
            _good_evidence(
                drawdown_pct=Decimal("0.06"),
                prev_period_was_scaled=True,
            )
        )
        # 0.06 × 2 = 0.12 > 0.10 → não elegível
        assert result.eligible is False
        assert any("drawdown" in m for m in result.missing_criteria)


# ---------------------------------------------------------------------------
# Incremento +1
# ---------------------------------------------------------------------------
class TestIncrementalStep:
    def test_increment_plus_1_ok(self):
        validate_incremental_step("WIN", 2, 3)

    def test_increment_plus_2_raises(self):
        with pytest.raises(IncrementalViolationError):
            validate_incremental_step("WIN", 2, 4)

    def test_ceiling_blocks_above_max_win(self):
        with pytest.raises(BlockedByCeilingError):
            validate_incremental_step("WIN", MAX_SCALED_WIN, MAX_SCALED_WIN + 1)

    def test_ceiling_blocks_above_max_wdo(self):
        with pytest.raises(BlockedByCeilingError):
            validate_incremental_step("WDO", MAX_SCALED_WDO, MAX_SCALED_WDO + 1)


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------
class TestCooldown:
    def test_default_7_days(self):
        assert compute_cooldown_days(0) == COOLDOWN_DEFAULT_DAYS

    def test_win_streak_21_days(self):
        assert detect_win_streak(5) is True
        assert compute_cooldown_days(5) == COOLDOWN_WIN_STREAK_DAYS

    def test_under_streak_threshold_is_7(self):
        assert compute_cooldown_days(3) == COOLDOWN_DEFAULT_DAYS


# ---------------------------------------------------------------------------
# Constants blindagem
# ---------------------------------------------------------------------------
class TestCeilingConstants:
    def test_max_scaled_win_is_5(self):
        assert MAX_SCALED_WIN == 5

    def test_max_scaled_wdo_is_5(self):
        assert MAX_SCALED_WDO == 5


# ---------------------------------------------------------------------------
# Repository
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
async def clean():
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        await conn.execute(
            _text("DELETE FROM cam_constitutional_scaling_events")
        )
    yield


@pytestmark_db
async def test_repository_insert_eligibility_ready(clean):
    repo = ScalingEventsRepository()
    sid = uuid4()
    async with async_session_factory() as session:
        evt_id = await repo.insert(
            session,
            event_type="ELIGIBILITY_READY",
            strategy_id=sid,
            evidence_json=_good_evidence().to_dict(),
        )
    assert evt_id is not None


@pytestmark_db
async def test_repository_rejects_invalid_event_type(clean):
    repo = ScalingEventsRepository()
    async with async_session_factory() as session:
        with pytest.raises(ValueError):
            await repo.insert(session, event_type="BAD_TYPE")


@pytestmark_db
async def test_repository_latest_in_force_returns_none_if_reverted(clean):
    repo = ScalingEventsRepository()
    sid = uuid4()
    async with async_session_factory() as session:
        await repo.insert(
            session,
            event_type="IN_FORCE",
            strategy_id=sid,
            proposed_limit_win=3,
        )
    async with async_session_factory() as session:
        await repo.insert(
            session,
            event_type="AUTO_REVERTED",
            strategy_id=sid,
        )
    async with async_session_factory() as session:
        latest = await repo.latest_in_force(session, sid)
    assert latest is None


@pytestmark_db
async def test_repository_blocked_attempt_persisted(clean):
    repo = ScalingEventsRepository()
    sid = uuid4()
    async with async_session_factory() as session:
        evt_id = await repo.insert(
            session,
            event_type="BLOCKED_ATTEMPT",
            strategy_id=sid,
            proposed_limit_win=4,
            notes="incremental violation 2→4",
        )
    assert evt_id is not None
