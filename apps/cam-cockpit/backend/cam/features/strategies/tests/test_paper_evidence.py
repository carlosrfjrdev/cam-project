"""TDD First — paper_evidence (TASK-019 BL-C)."""
from __future__ import annotations

import os
import subprocess
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.domain.primitives import AssetType
from cam._shared.infra import async_session_factory, engine
from cam.features.strategies.domain import StrategyMetadata, StrategyStatus
from cam.features.strategies.paper_evidence import (
    PaperOkPrerequisitesError,
    build_paper_evidence,
)
from cam.features.strategies.repository import StrategyRepository

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL

pytestmark = pytest.mark.skipif(
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
        await conn.execute(_text("DELETE FROM cam_paper_trades"))
        await conn.execute(_text("DELETE FROM cam_evidence_packs"))
        await conn.execute(_text("DELETE FROM cam_strategies"))
    yield


async def _register_strategy() -> UUID:
    repo = StrategyRepository()
    async with async_session_factory() as session:
        return await repo.register(
            session,
            StrategyMetadata(
                id=uuid4(),
                name="S1 ORB Test",
                version="1.0.0",
                asset=AssetType.WIN,
                author="test",
            ),
        )


async def _insert_paper_trades(
    strategy_id: UUID,
    count: int,
    approved: int,
    adherence: Decimal,
) -> None:
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        for i in range(count):
            is_approved = i < approved
            await conn.execute(
                _text(
                    "INSERT INTO cam_paper_trades "
                    "(id, session_id, asset, direction, contracts, entry_price, "
                    " result_gross, risk_decision, strategy_id, intent_id, "
                    " adherence, ts_open, ts_close) "
                    "VALUES (gen_random_uuid(), gen_random_uuid(), 'WIN', "
                    "        'LONG', 1, 130000, 0, :rd, :sid, "
                    "        gen_random_uuid(), :adh, NOW(), NOW())"
                ),
                {
                    "rd": "APPROVED" if is_approved else "REJECTED",
                    "sid": str(strategy_id),
                    "adh": str(adherence if is_approved else 0),
                },
            )


async def test_build_evidence_fails_with_under_100_trades(clean):
    sid = await _register_strategy()
    await _insert_paper_trades(sid, count=50, approved=50, adherence=Decimal("0.98"))
    async with async_session_factory() as session:
        with pytest.raises(PaperOkPrerequisitesError):
            await build_paper_evidence(session, sid)


async def test_build_evidence_fails_with_low_adherence(clean):
    sid = await _register_strategy()
    await _insert_paper_trades(
        sid, count=120, approved=120, adherence=Decimal("0.85"),
    )
    async with async_session_factory() as session:
        with pytest.raises(PaperOkPrerequisitesError) as ei:
            await build_paper_evidence(session, sid)
    assert "adherence" in str(ei.value)


async def test_build_evidence_succeeds_with_100_and_95(clean):
    sid = await _register_strategy()
    await _insert_paper_trades(
        sid, count=100, approved=100, adherence=Decimal("0.96"),
    )
    async with async_session_factory() as session:
        pack = await build_paper_evidence(session, sid)
    assert pack.status_target == StrategyStatus.PAPER_OK
    assert pack.adherence >= Decimal("0.95")
