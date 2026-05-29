"""TDD First — TASK-041 (BL-G): provider governance + OpenAI block."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import pytest_asyncio

from cam._shared.config import settings
from cam._shared.infra import async_session_factory, engine
from cam.features.ai_analyst.provider_governance import (
    OpenAINotEnabledError,
    Provider,
    call_provider,
)

BACKEND_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL") or settings.database_url or ""


_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


class TestProviderBlocking:
    @pytest.mark.asyncio
    async def test_openai_raises_not_enabled(self):
        with pytest.raises(OpenAINotEnabledError):
            await call_provider(Provider.OPENAI, "prompt")

    @pytest.mark.asyncio
    async def test_anthropic_does_not_raise(self):
        record = await call_provider(
            Provider.ANTHROPIC,
            "prompt",
            response="response",
            session=None,
        )
        assert record.provider is Provider.ANTHROPIC
        assert len(record.prompt_hash) == 64


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
async def test_anthropic_call_persists_record():
    from sqlalchemy import text as _text

    async with engine.begin() as conn:
        await conn.execute(_text("DELETE FROM cam_ai_provider_calls"))

    async with async_session_factory() as session:
        record = await call_provider(
            Provider.ANTHROPIC,
            "prompt",
            response="r",
            session=session,
        )
    async with engine.begin() as conn:
        result = await conn.execute(
            _text("SELECT COUNT(*) FROM cam_ai_provider_calls")
        )
        count = result.scalar()
    assert count == 1
