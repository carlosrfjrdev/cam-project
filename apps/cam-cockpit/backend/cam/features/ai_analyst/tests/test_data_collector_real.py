"""TDD First — AIAnalystDataCollector real DB (TASK-018 BL-C)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory
from cam.features.ai_analyst.data_collector import AnalystDataCollector

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Sem session_factory — comportamento legacy
# ---------------------------------------------------------------------------
class TestLegacyMode:
    @pytest.mark.asyncio
    async def test_no_session_factory_returns_empty_lists(self):
        collector = AnalystDataCollector(session_factory=None)
        assert await collector.get_journal_entries_today("2026-05-27") == []
        assert await collector.get_risk_decisions_today("2026-05-27") == []
        assert await collector.get_violations_today("2026-05-27") == []


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


@pytestmark_db
async def test_collector_queries_journal_table_for_date():
    """Mesmo sem dados, query roda sem erro de schema."""
    collector = AnalystDataCollector(session_factory=async_session_factory)
    result = await collector.get_journal_entries_today("2026-05-27")
    assert isinstance(result, list)


@pytestmark_db
async def test_aggregate_metrics_today_returns_dict():
    collector = AnalystDataCollector(session_factory=async_session_factory)
    agg = await collector.aggregate_metrics_today("2026-05-27")
    assert "total_trades" in agg
    assert "decisions_approved" in agg
    assert "decisions_rejected" in agg
