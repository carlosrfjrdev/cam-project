"""TDD First — Paper Loop Governado (TASK-016/017 BL-C)."""
from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio

from cam._shared.config import Settings, settings
from cam._shared.domain.primitives import AssetType, ContractCount, Direction
from cam._shared.infra import async_session_factory
from cam._shared.order_gateway.gateway import OrderGateway
from cam._shared.risk.context import OrderCandidate
from cam.features.paper_trading.loop import PaperTradingLoop
from cam.features.strategies.domain import StrategyContext, StrategyMetadata

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    env_var = os.getenv("DATABASE_URL")
    if env_var:
        return env_var
    return settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


# ---------------------------------------------------------------------------
# Strategy stub: dispara LONG no 1º tick "trigger=True"
# ---------------------------------------------------------------------------
class _AlwaysTriggerStrategy:
    def __init__(self):
        self.metadata = StrategyMetadata(
            id=uuid4(),
            name="dummy",
            version="0.0.1",
            asset=AssetType.WIN,
            author="test",
        )

    def evaluate(self, tick, context):
        if tick.get("trigger"):
            return OrderCandidate(
                asset=AssetType.WIN,
                direction=Direction.LONG,
                contracts=ContractCount(1),
                intended_stop_loss_points=Decimal("150"),
                is_setup_a_plus=True,
            )
        return None


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
async def clean_paper():
    from sqlalchemy import text as _text

    from cam._shared.infra import engine

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_paper_trades"))
    yield


def _ticks(n=3, trigger_at=0):
    base = datetime(2026, 5, 27, 11, 0, tzinfo=timezone.utc)
    from datetime import timedelta as _td
    return [
        {
            "timestamp": base + _td(seconds=i),
            "price": 130000 + i * 10,
            "trigger": (i == trigger_at),
        }
        for i in range(n)
    ]


@pytestmark_db
async def test_loop_persists_paper_trade_after_approval(clean_paper):
    strategy = _AlwaysTriggerStrategy()
    gateway = OrderGateway(settings=Settings(_env_file=None))
    loop = PaperTradingLoop(strategy, gateway, async_session_factory)
    stats = await loop.run(_ticks(), strategy_id=strategy.metadata.id)

    assert stats.candidates_emitted == 1
    assert stats.approved == 1

    # Verificar persistência
    from sqlalchemy import text as _text
    from cam._shared.infra import engine
    async with engine.begin() as conn:
        result = await conn.execute(
            _text(
                "SELECT COUNT(*) FROM cam_paper_trades "
                "WHERE strategy_id = :sid"
            ),
            {"sid": str(strategy.metadata.id)},
        )
        count = result.scalar()
    assert count == 1


@pytestmark_db
async def test_kill_switch_stops_loop_under_1s(clean_paper):
    strategy = _AlwaysTriggerStrategy()
    gateway = OrderGateway(settings=Settings(_env_file=None))
    loop = PaperTradingLoop(strategy, gateway, async_session_factory)

    # Aciona kill switch antes de rodar — loop deve sair na 1ª iteração
    loop.kill_switch.set()
    import time as _time
    t0 = _time.monotonic()
    stats = await loop.run(_ticks(n=100), strategy_id=strategy.metadata.id)
    elapsed = _time.monotonic() - t0

    assert stats.stop_reason == "kill_switch"
    assert elapsed < 1.0  # CA-C.2
    assert stats.kill_switch_at is not None


@pytestmark_db
async def test_loop_emits_audit_per_intent(clean_paper):
    strategy = _AlwaysTriggerStrategy()
    gateway = OrderGateway(settings=Settings(_env_file=None))
    loop = PaperTradingLoop(strategy, gateway, async_session_factory)
    from datetime import timedelta as _td
    base = datetime(2026, 5, 27, 11, 0, tzinfo=timezone.utc)
    ticks = [
        {"timestamp": base + _td(seconds=i),
         "price": 130000, "trigger": True}
        for i in range(3)
    ]
    stats = await loop.run(ticks, strategy_id=strategy.metadata.id)
    # 3 candidates emitidos; persistência separa intent_id distinto
    assert stats.candidates_emitted == 3

    from sqlalchemy import text as _text
    from cam._shared.infra import engine
    async with engine.begin() as conn:
        result = await conn.execute(
            _text(
                "SELECT COUNT(DISTINCT intent_id) FROM cam_paper_trades "
                "WHERE strategy_id = :sid"
            ),
            {"sid": str(strategy.metadata.id)},
        )
        unique_intents = result.scalar()
    assert unique_intents == 3
