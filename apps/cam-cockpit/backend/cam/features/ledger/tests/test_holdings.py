"""TDD First — BL-D: Holdings + Genial integration + assert risco."""
from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam.features.ledger.genial_importer import parse_extrato
from cam.features.ledger.holdings import (
    GenialHoldingsService,
    HoldingIn,
    HoldingsRepository,
    HoldingValidationError,
    InvalidAssetForRiskError,
    assert_can_add_to_risk,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent
FIXTURES = BACKEND_ROOT / "tests" / "fixtures"


def _get_db_url() -> str:
    env_var = os.getenv("DATABASE_URL")
    if env_var:
        return env_var
    return settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------
class TestAssertCanAddToRisk:
    def test_PETR4_rejected(self):
        with pytest.raises(InvalidAssetForRiskError) as ei:
            assert_can_add_to_risk("PETR4")
        assert "Art. 23" in str(ei.value)

    def test_WIN_accepted(self):
        assert_can_add_to_risk("WIN")

    def test_WDO_accepted(self):
        assert_can_add_to_risk("WDO")

    def test_lower_case_normalized(self):
        with pytest.raises(InvalidAssetForRiskError):
            assert_can_add_to_risk("itub4")


class TestValidation:
    def test_invalid_source_rejected(self):
        with pytest.raises(HoldingValidationError):
            from cam.features.ledger.holdings import _validate
            _validate(
                HoldingIn(
                    ticker="PETR4",
                    quantity=Decimal("10"),
                    avg_price=Decimal("35"),
                    source="BAD_SOURCE",
                )
            )


# ---------------------------------------------------------------------------
# DB integration
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
    assert result.returncode == 0, f"Alembic upgrade failed:\n{result.stderr}"
    yield


@pytest_asyncio.fixture
async def clean_holdings():
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_carteira_hard_holdings"))
    yield


@pytestmark_db
async def test_create_holding_manual_ui(clean_holdings):
    repo = HoldingsRepository()
    async with async_session_factory() as session:
        sid = await repo.create(
            session,
            HoldingIn(
                ticker="PETR4",
                quantity=Decimal("100"),
                avg_price=Decimal("35.50"),
                source="MANUAL_UI",
            ),
        )
    assert sid is not None
    assert isinstance(sid, UUID)


@pytestmark_db
async def test_duplicate_holding_returns_none(clean_holdings):
    repo = HoldingsRepository()
    h = HoldingIn(
        ticker="ITUB4",
        quantity=Decimal("200"),
        avg_price=Decimal("28.90"),
        acquired_at=datetime(2026, 1, 15, tzinfo=UTC),
        source="MANUAL_UI",
    )
    async with async_session_factory() as session:
        sid1 = await repo.create(session, h)
    async with async_session_factory() as session:
        sid2 = await repo.create(session, h)
    assert sid1 is not None
    assert sid2 is None  # dup


@pytestmark_db
async def test_genial_import_5_tickers(clean_holdings):
    parsed = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
    service = GenialHoldingsService()
    async with async_session_factory() as session:
        result = await service.import_from_parsed(session, parsed)
    assert result["created"] == 5
    assert result["duplicated"] == 0


@pytestmark_db
async def test_genial_reimport_dedup(clean_holdings):
    parsed = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
    service = GenialHoldingsService()
    async with async_session_factory() as session:
        await service.import_from_parsed(session, parsed)
    async with async_session_factory() as session:
        r2 = await service.import_from_parsed(session, parsed)
    assert r2["created"] == 0
    assert r2["duplicated"] == 5


@pytestmark_db
async def test_check_constraint_quantity_positive(clean_holdings):
    """DB rejeita quantity ≤ 0 mesmo se o validator Python falhar."""
    from sqlalchemy import text as _text
    from sqlalchemy.exc import IntegrityError

    async with engine.begin() as conn:
        with pytest.raises(IntegrityError):
            await conn.execute(
                _text(
                    "INSERT INTO cam_carteira_hard_holdings "
                    "(ticker, asset_class, quantity, avg_price, source, hash) "
                    "VALUES ('PETR4', 'equity', 0, 35.50, 'MANUAL_UI', 'h1')"
                )
            )
