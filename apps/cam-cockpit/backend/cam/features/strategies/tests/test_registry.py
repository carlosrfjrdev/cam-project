"""
TDD First — testes do StrategyRegistry (TASK-002 BL-A).

Testes de unidade são skippados se DB não disponível (segue padrão
de tests/test_migrations.py). Em CI com DB rodando, validam:
  - register persiste com status=draft, is_active=false.
  - register de duplicado (name, version) levanta StrategyAlreadyExistsError.
  - list retorna em ordem cronológica.
  - set_active troca atomicamente o ativo.
  - constraint DB rejeita 2 ativas simultâneas (forçando via SQL raw).
  - update_status valida transição.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from cam._shared.config import settings
from cam._shared.domain.primitives import AssetType
from cam._shared.infra import async_session_factory, engine
from cam.features.strategies.domain import StrategyMetadata, StrategyStatus
from cam.features.strategies.repository import (
    InvalidStatusTransitionError,
    StrategyAlreadyExistsError,
    StrategyNotFoundError,
    StrategyRepository,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    env_var = os.getenv("DATABASE_URL")
    if env_var:
        return env_var
    return settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


pytestmark = pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco de dados configurado (DATABASE_URL no ambiente)",
)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _ensure_migrations_up():
    """Garante migration HEAD antes dos testes do módulo."""
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
async def clean_strategies():
    """Limpa cam_strategies e cam_evidence_packs entre testes."""
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM cam_evidence_packs"))
        await conn.execute(text("DELETE FROM cam_strategies"))
    yield


def _make_metadata(name: str = "S1 ORB", version: str = "1.0.0") -> StrategyMetadata:
    return StrategyMetadata(
        id=uuid4(),
        name=name,
        version=version,
        asset=AssetType.WIN,
        author="Carlos",
        custom_metrics={"opening_range_minutes": 60},
    )


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------
async def test_register_persists_metadata_with_default_status_draft(
    clean_strategies,
):
    repo = StrategyRepository()
    meta = _make_metadata()
    async with async_session_factory() as session:
        sid = await repo.register(session, meta)
    async with async_session_factory() as session:
        row = await repo.get(session, sid)
    assert row["status"] == "draft"
    assert row["is_active"] is False
    assert row["name"] == "S1 ORB"
    assert row["metadata_json"]["opening_range_minutes"] == 60


async def test_register_duplicate_name_version_raises(clean_strategies):
    repo = StrategyRepository()
    meta = _make_metadata()
    async with async_session_factory() as session:
        await repo.register(session, meta)
    async with async_session_factory() as session:
        with pytest.raises(StrategyAlreadyExistsError):
            await repo.register(session, _make_metadata())


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
async def test_list_returns_in_insertion_order(clean_strategies):
    repo = StrategyRepository()
    async with async_session_factory() as session:
        await repo.register(session, _make_metadata("S1 ORB", "1.0.0"))
        await repo.register(session, _make_metadata("S2 RSI", "1.0.0"))
    async with async_session_factory() as session:
        all_strategies = await repo.list_all(session)
    assert [s["name"] for s in all_strategies] == ["S1 ORB", "S2 RSI"]


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------
async def test_get_unknown_raises_not_found(clean_strategies):
    repo = StrategyRepository()
    async with async_session_factory() as session:
        with pytest.raises(StrategyNotFoundError):
            await repo.get(session, uuid4())


# ---------------------------------------------------------------------------
# set_active — defesa estrutural
# ---------------------------------------------------------------------------
async def test_set_active_deactivates_previous_active(clean_strategies):
    repo = StrategyRepository()
    async with async_session_factory() as session:
        sid1 = await repo.register(session, _make_metadata("S1 ORB", "1.0.0"))
        sid2 = await repo.register(session, _make_metadata("S2 RSI", "1.0.0"))

    async with async_session_factory() as session:
        await repo.set_active(session, sid1)
    async with async_session_factory() as session:
        await repo.set_active(session, sid2)

    async with async_session_factory() as session:
        all_strategies = await repo.list_all(session)
    active_count = sum(1 for s in all_strategies if s["is_active"])
    assert active_count == 1
    active = next(s for s in all_strategies if s["is_active"])
    assert UUID(str(active["id"])) == sid2


async def test_constraint_db_rejects_two_active_via_direct_sql(
    clean_strategies,
):
    """
    Defesa em profundidade: mesmo se um caller burlar o repository e tentar
    UPDATE direto setando is_active=true em uma 2ª linha, o índice parcial
    único deve barrar.
    """
    repo = StrategyRepository()
    async with async_session_factory() as session:
        sid1 = await repo.register(session, _make_metadata("S1 ORB", "1.0.0"))
        sid2 = await repo.register(session, _make_metadata("S2 RSI", "1.0.0"))

    async with async_session_factory() as session:
        await repo.set_active(session, sid1)

    async with engine.begin() as conn:
        with pytest.raises(IntegrityError):
            await conn.execute(
                text(
                    "UPDATE cam_strategies SET is_active = true WHERE id = :id"
                ),
                {"id": str(sid2)},
            )


# ---------------------------------------------------------------------------
# update_status
# ---------------------------------------------------------------------------
async def test_update_status_valid_forward_transition(clean_strategies):
    repo = StrategyRepository()
    async with async_session_factory() as session:
        sid = await repo.register(session, _make_metadata())
    async with async_session_factory() as session:
        await repo.update_status(session, sid, StrategyStatus.BACKTESTED)
    async with async_session_factory() as session:
        row = await repo.get(session, sid)
    assert row["status"] == "backtested"


async def test_update_status_invalid_skip_raises(clean_strategies):
    repo = StrategyRepository()
    async with async_session_factory() as session:
        sid = await repo.register(session, _make_metadata())
    async with async_session_factory() as session:
        with pytest.raises(InvalidStatusTransitionError):
            await repo.update_status(session, sid, StrategyStatus.DEMO_OK)


# ---------------------------------------------------------------------------
# to_metadata helper
# ---------------------------------------------------------------------------
async def test_to_metadata_round_trip(clean_strategies):
    repo = StrategyRepository()
    meta_in = _make_metadata()
    async with async_session_factory() as session:
        sid = await repo.register(session, meta_in)
    async with async_session_factory() as session:
        row = await repo.get(session, sid)
    meta_out = StrategyRepository.to_metadata(row)
    assert meta_out.name == meta_in.name
    assert meta_out.asset is AssetType.WIN
    assert meta_out.custom_metrics["opening_range_minutes"] == 60
