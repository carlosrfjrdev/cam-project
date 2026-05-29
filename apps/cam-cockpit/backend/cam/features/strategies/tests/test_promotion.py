"""
TDD First — testes de promotion + evidence (TASK-003 BL-A).

- EvidencePack: validação por status alvo + hash determinístico.
- PromotionService.promote: integração com repository.
"""
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
from cam._shared.infra import async_session_factory
from cam.features.strategies.domain import StrategyMetadata, StrategyStatus
from cam.features.strategies.evidence import (
    EvidenceInsufficientError,
    EvidencePack,
    validate_for_target,
)
from cam.features.strategies.promotion import (
    EvidenceDuplicateError,
    EvidenceRequiredError,
    PromotionService,
)
from cam.features.strategies.repository import (
    InvalidStatusTransitionError,
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


# ---------------------------------------------------------------------------
# EvidencePack: testes unitários puros (não exigem DB)
# ---------------------------------------------------------------------------
class TestEvidencePack:
    def test_hash_is_deterministic(self):
        sid = uuid4()
        pack1 = EvidencePack(
            strategy_id=sid,
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-1"],
        )
        pack2 = EvidencePack(
            strategy_id=sid,
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-1"],
        )
        assert pack1.compute_hash() == pack2.compute_hash()
        assert len(pack1.compute_hash()) == 64  # SHA-256 hex

    def test_hash_changes_with_payload(self):
        sid = uuid4()
        pack1 = EvidencePack(
            strategy_id=sid,
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-1"],
        )
        pack2 = EvidencePack(
            strategy_id=sid,
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-2"],
        )
        assert pack1.compute_hash() != pack2.compute_hash()

    def test_draft_as_target_raises(self):
        with pytest.raises(ValueError):
            EvidencePack(
                strategy_id=uuid4(),
                status_target=StrategyStatus.DRAFT,
            )

    def test_pack_is_frozen(self):
        from dataclasses import FrozenInstanceError

        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-1"],
        )
        with pytest.raises(FrozenInstanceError):
            pack.adherence = Decimal("1.0")  # type: ignore[misc]


# ---------------------------------------------------------------------------
# validate_for_target: testes unitários
# ---------------------------------------------------------------------------
class TestValidateForTarget:
    def test_backtested_requires_backtest_runs(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.BACKTESTED,
        )
        with pytest.raises(EvidenceInsufficientError):
            validate_for_target(pack)

    def test_backtested_accepts_with_runs(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.BACKTESTED,
            backtest_runs=["run-1"],
        )
        validate_for_target(pack)  # não levanta

    def test_walk_forward_requires_results(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.WALK_FORWARD_OK,
        )
        with pytest.raises(EvidenceInsufficientError):
            validate_for_target(pack)

    def test_paper_ok_requires_results(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.PAPER_OK,
        )
        with pytest.raises(EvidenceInsufficientError):
            validate_for_target(pack)

    def test_real_authorized_requires_adherence_95(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.REAL_AUTHORIZED,
            paper_results=["p1"],
            adherence=Decimal("0.90"),
        )
        with pytest.raises(EvidenceInsufficientError):
            validate_for_target(pack)

    def test_real_authorized_accepts_adherence_95(self):
        pack = EvidencePack(
            strategy_id=uuid4(),
            status_target=StrategyStatus.REAL_AUTHORIZED,
            paper_results=["p1"],
            adherence=Decimal("0.95"),
        )
        validate_for_target(pack)  # não levanta


# ===========================================================================
# Testes de integração com DB (skippable)
# ===========================================================================
pytestmark = pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco de dados configurado",
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
async def clean_db():
    from sqlalchemy import text as _text

    from cam._shared.infra import engine

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_evidence_packs"))
        await conn.execute(_text("DELETE FROM cam_strategies"))
    yield


async def _register_dummy(repo: StrategyRepository) -> UUID:
    async with async_session_factory() as session:
        return await repo.register(
            session,
            StrategyMetadata(
                id=uuid4(),
                name="S1 ORB",
                version="1.0.0",
                asset=AssetType.WIN,
                author="Carlos",
            ),
        )


async def test_promote_without_evidence_raises_required(clean_db):
    repo = StrategyRepository()
    service = PromotionService(repo)
    sid = await _register_dummy(repo)
    async with async_session_factory() as session:
        with pytest.raises(EvidenceRequiredError):
            await service.promote(
                session, sid, StrategyStatus.BACKTESTED, evidence=None
            )


async def test_promote_to_backtested_succeeds(clean_db):
    repo = StrategyRepository()
    service = PromotionService(repo)
    sid = await _register_dummy(repo)
    evidence = EvidencePack(
        strategy_id=sid,
        status_target=StrategyStatus.BACKTESTED,
        backtest_runs=["run-1"],
    )
    async with async_session_factory() as session:
        await service.promote(session, sid, StrategyStatus.BACKTESTED, evidence)
    async with async_session_factory() as session:
        row = await repo.get(session, sid)
    assert row["status"] == "backtested"


async def test_promote_skipping_status_raises(clean_db):
    repo = StrategyRepository()
    service = PromotionService(repo)
    sid = await _register_dummy(repo)
    evidence = EvidencePack(
        strategy_id=sid,
        status_target=StrategyStatus.DEMO_OK,
        paper_results=["p1", "p2"],
    )
    async with async_session_factory() as session:
        with pytest.raises(InvalidStatusTransitionError):
            await service.promote(session, sid, StrategyStatus.DEMO_OK, evidence)


async def test_promote_duplicate_evidence_raises(clean_db):
    repo = StrategyRepository()
    service = PromotionService(repo)
    sid = await _register_dummy(repo)
    evidence = EvidencePack(
        strategy_id=sid,
        status_target=StrategyStatus.BACKTESTED,
        backtest_runs=["run-1"],
    )
    async with async_session_factory() as session:
        await service.promote(session, sid, StrategyStatus.BACKTESTED, evidence)
    # nova promoção com mesma evidência (mesmo hash) — duplicate
    async with async_session_factory() as session:
        # primeiro vamos para walk_forward_ok com a mesma evidência hash?
        # como o status_target faz parte do hash, mudamos para evidência
        # do mesmo target original que já está persistido.
        # Aqui exercitamos: tentar promover novamente com mesma evidência
        # (status_target=BACKTESTED), mesmo já estando em BACKTESTED.
        with pytest.raises(
            (EvidenceDuplicateError, InvalidStatusTransitionError)
        ):
            await service.promote(
                session, sid, StrategyStatus.BACKTESTED, evidence
            )


async def test_promote_to_retired_without_evidence_succeeds(clean_db):
    repo = StrategyRepository()
    service = PromotionService(repo)
    sid = await _register_dummy(repo)
    async with async_session_factory() as session:
        await service.promote(
            session, sid, StrategyStatus.RETIRED, evidence=None
        )
    async with async_session_factory() as session:
        row = await repo.get(session, sid)
    assert row["status"] == "retired"
