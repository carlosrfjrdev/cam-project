"""
T-A07/A08/A09 — Testes de migrations Alembic.
Requerem banco de dados configurado via DATABASE_URL.
"""
import os
import subprocess
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).parent.parent

# Lê DATABASE_URL do ambiente OU do .env via settings (pydantic-settings carrega .env)
def _get_db_url() -> str:
    env_var = os.getenv("DATABASE_URL")
    if env_var:
        return env_var
    try:
        from cam._shared.config import settings
        return settings.database_url
    except Exception:
        return ""

_DB_URL = _get_db_url()
DB_AVAILABLE = bool(_DB_URL) and "localhost" in _DB_URL


@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco de dados configurado (DATABASE_URL no ambiente)",
)
def test_migrations_run_clean():
    env = {**os.environ, "DATABASE_URL": _DB_URL}
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_ROOT),
        env=env,
    )
    assert result.returncode == 0, f"Migration failed:\n{result.stderr}"


@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco configurado",
)
def test_operational_tables_exist():
    import asyncio

    from sqlalchemy import text

    from cam._shared.infra import engine

    async def check():
        async with engine.begin() as conn:
            for table in [
                "cam_orders",
                "cam_trades",
                "cam_journal_entries",
                "cam_risk_decisions",
                "cam_violations",
                "cam_kill_switch_events",
                "cam_checklist_pre_market",
                "cam_checklist_post_market",
                "cam_constitution_versions",
                "cam_phase_history",
            ]:
                result = await conn.execute(
                    text(f"SELECT to_regclass('public.{table}')")
                )
                assert result.scalar() is not None, f"Table missing: {table}"

    asyncio.run(check())


@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco configurado",
)
def test_fiscal_patrimonial_tables_exist():
    import asyncio

    from sqlalchemy import text

    from cam._shared.infra import engine

    async def check():
        async with engine.begin() as conn:
            for table in [
                "cam_fiscal_apuration",
                "cam_darf_history",
                "cam_loss_compensation_ledger",
                "cam_bucket_transactions",
                "cam_harvest_history",
                "cam_backtest_runs",
                "cam_backtest_trades",
                "cam_backtest_equity_curve",
                "cam_pattern_studies",
                "cam_paper_trades",
                "cam_ai_analysis",
            ]:
                result = await conn.execute(
                    text(f"SELECT to_regclass('public.{table}')")
                )
                assert result.scalar() is not None, f"Table missing: {table}"

    asyncio.run(check())


@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Requer banco configurado",
)
def test_hypertables_exist():
    import asyncio

    from sqlalchemy import text

    from cam._shared.infra import engine

    async def check():
        async with engine.begin() as conn:
            query = (
                "SELECT hypertable_name "
                "FROM timescaledb_information.hypertables "
                "WHERE hypertable_name IN "
                "('cam_market_ticks', 'cam_market_book_snapshots')"
            )
            result = await conn.execute(text(query))
            hypertables = {row[0] for row in result.fetchall()}
            assert "cam_market_ticks" in hypertables, (
                "cam_market_ticks not a hypertable"
            )
            assert "cam_market_book_snapshots" in hypertables, (
                "cam_market_book_snapshots not a hypertable"
            )

    asyncio.run(check())
