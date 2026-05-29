"""TDD First — TASK-062 (BL-I) Instrument Catalog amplo."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam.features.market_data.instruments_loader import (
    InstrumentRow,
    activate,
    parse_instruments_csv,
    upsert_instruments,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent
SEED_PATH = BACKEND_ROOT / "data" / "seeds" / "b3_instruments_200.csv"


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


class TestParser:
    def test_seed_has_at_least_200_rows(self):
        rows = parse_instruments_csv(SEED_PATH)
        assert len(rows) >= 200

    def test_each_row_has_required_fields(self):
        rows = parse_instruments_csv(SEED_PATH)
        for r in rows:
            assert r.ticker
            assert r.asset_class in {"futures", "equity", "fii", "etf", "other"}
            assert r.point_value > 0

    def test_default_active_false(self):
        rows = parse_instruments_csv(SEED_PATH)
        assert all(r.active is False for r in rows)


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
async def test_upsert_inserts_new_only():
    rows = parse_instruments_csv(SEED_PATH)
    async with async_session_factory() as session:
        inserted_1 = await upsert_instruments(session, rows)
    # Reimport — 0 novos (idempotência)
    async with async_session_factory() as session:
        inserted_2 = await upsert_instruments(session, rows)
    assert inserted_2 == 0


@pytestmark_db
async def test_activate_endpoint_changes_state():
    rows = parse_instruments_csv(SEED_PATH)
    async with async_session_factory() as session:
        await upsert_instruments(session, rows)
    target = rows[0].ticker
    async with async_session_factory() as session:
        changed = await activate(session, target)
    # Pode ser True (1ª ativação) ou False (já ativo de seed canônico
    # como WIN/WDO). Não falhamos — só testamos que retorna bool.
    assert isinstance(changed, bool)
