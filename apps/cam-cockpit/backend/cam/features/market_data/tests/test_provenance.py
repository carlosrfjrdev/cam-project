"""
TDD First — TASK-011/012/013 BL-B.

Cobre:
- compute_quality_flags: gaps, zero volume, out of hours.
- compute_batch_hash: determinismo.
- ingest_ticks: provenance, dedup, license, vazio.

Testes que exigem DB são skippados se DATABASE_URL não disponível.
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam.features.market_data.provenance import (
    LicenseNotAckError,
    MarketDataService,
    ProvenanceInput,
    TickRow,
    compute_batch_hash,
    compute_quality_flags,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    env_var = os.getenv("DATABASE_URL")
    if env_var:
        return env_var
    return settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Unit tests (sem DB)
# ---------------------------------------------------------------------------
def _t(h: int, m: int = 0, *, vol: int = 100, asset: str = "WIN") -> TickRow:
    return TickRow(
        asset=asset,
        timestamp=datetime(2026, 5, 27, h, m, tzinfo=timezone.utc),
        price=Decimal("130000"),
        volume=vol,
    )


class TestQualityFlags:
    def test_empty_returns_safe_defaults(self):
        flags = compute_quality_flags([])
        assert flags["has_gaps"] is False
        assert flags["has_zero_volume"] is False
        assert flags["out_of_hours"] is False

    def test_zero_volume_detected(self):
        flags = compute_quality_flags([_t(10), _t(11, vol=0)])
        assert flags["has_zero_volume"] is True

    def test_gaps_detected_above_threshold(self):
        # 5 min de gap → has_gaps True
        ticks = [
            TickRow(
                "WIN",
                datetime(2026, 5, 27, 10, 0, tzinfo=timezone.utc),
                Decimal("130000"),
                10,
            ),
            TickRow(
                "WIN",
                datetime(2026, 5, 27, 10, 5, tzinfo=timezone.utc),
                Decimal("130000"),
                10,
            ),
        ]
        assert compute_quality_flags(ticks)["has_gaps"] is True

    def test_continuous_data_no_gap(self):
        ticks = [
            TickRow(
                "WIN",
                datetime(2026, 5, 27, 10, 0, s, tzinfo=timezone.utc),
                Decimal("130000"),
                10,
            )
            for s in (0, 10, 20, 30)
        ]
        assert compute_quality_flags(ticks)["has_gaps"] is False

    def test_out_of_hours_detected(self):
        # 20h UTC → fora do pregão B3 09:00-18:30
        ticks = [_t(20)]
        assert compute_quality_flags(ticks)["out_of_hours"] is True

    def test_in_hours_not_flagged(self):
        ticks = [_t(10), _t(15)]
        assert compute_quality_flags(ticks)["out_of_hours"] is False


class TestBatchHash:
    def test_hash_deterministic_same_input(self):
        ticks = [_t(10), _t(11)]
        assert compute_batch_hash(ticks, "test_source") == compute_batch_hash(
            ticks, "test_source"
        )

    def test_hash_changes_with_source(self):
        ticks = [_t(10)]
        assert compute_batch_hash(ticks, "s1") != compute_batch_hash(ticks, "s2")

    def test_hash_changes_with_ticks(self):
        h1 = compute_batch_hash([_t(10)], "s")
        h2 = compute_batch_hash([_t(11)], "s")
        assert h1 != h2

    def test_hash_invariant_to_order(self):
        ticks_a = [_t(10), _t(11)]
        ticks_b = [_t(11), _t(10)]
        # Hash interno ordena por (asset, ts) — deve ser idêntico
        assert compute_batch_hash(ticks_a, "s") == compute_batch_hash(ticks_b, "s")


class TestLicenseGate:
    @pytest.mark.asyncio
    async def test_ingest_fails_without_license_ack(self):
        service = MarketDataService()
        # Não chama DB porque levanta antes
        with pytest.raises(LicenseNotAckError):
            await service.ingest_ticks(
                session=None,  # type: ignore[arg-type]
                ticks=[_t(10)],
                provenance=ProvenanceInput(
                    source="test", license_terms_ack=False
                ),
            )


# ---------------------------------------------------------------------------
# Integração com DB
# ---------------------------------------------------------------------------
pytestmark_db = pytest.mark.skipif(
    not DB_AVAILABLE, reason="Requer DATABASE_URL configurado"
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
async def clean_provenance():
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_market_ticks"))
        await conn.execute(_text("DELETE FROM cam_market_data_provenance"))
    yield


@pytestmark_db
async def test_ingest_persists_provenance_and_ticks(clean_provenance):
    service = MarketDataService()
    ticks = [_t(10), _t(10, m=1), _t(10, m=2)]
    async with async_session_factory() as session:
        result = await service.ingest_ticks(
            session=session,
            ticks=ticks,
            provenance=ProvenanceInput(source="test", license_terms_ack=True),
        )
    assert result.import_id is not None
    assert result.tick_count == 3
    assert result.duplicated is False
    assert "has_zero_volume" in result.quality_flags


@pytestmark_db
async def test_reingest_same_batch_is_dedup(clean_provenance):
    service = MarketDataService()
    ticks = [_t(10)]
    async with async_session_factory() as session:
        r1 = await service.ingest_ticks(
            session,
            ticks,
            ProvenanceInput(source="test", license_terms_ack=True),
        )
    async with async_session_factory() as session:
        r2 = await service.ingest_ticks(
            session,
            ticks,
            ProvenanceInput(source="test", license_terms_ack=True),
        )
    assert r1.import_id is not None
    assert r2.duplicated is True
    assert r2.import_id is None


@pytestmark_db
async def test_seed_instruments_present():
    """Migration seed garante WIN/WDO/IND/DOL presentes (CA-B.4)."""
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        result = await conn.execute(
            _text("SELECT ticker, point_value FROM cam_instruments ORDER BY ticker")
        )
        rows = result.fetchall()
    tickers = {r[0] for r in rows}
    assert {"WIN", "WDO", "IND", "DOL"}.issubset(tickers)
    # point_value canônico (CA-B.4)
    pv = {r[0]: Decimal(str(r[1])) for r in rows}
    assert pv["WIN"] == Decimal("0.2000")
    assert pv["WDO"] == Decimal("10.0000")
