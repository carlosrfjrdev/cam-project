"""Inspetor — cam_inspector_candles (daily) for regime overlay

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-06-01

SPEC-Inspetor (ADR-014) — tabela regular de candles diários alimentada pelo
endpoint /mt5/candles (timeframe=D1) e lida pelo slice `regime`. Tabela regular
(não é continuous aggregate), upsert por (symbol, timeframe, ts).
"""
from collections.abc import Sequence

from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS cam_inspector_candles (
            symbol     TEXT        NOT NULL,
            timeframe  TEXT        NOT NULL,
            ts         TIMESTAMPTZ NOT NULL,
            open       NUMERIC(18, 6) NOT NULL,
            high       NUMERIC(18, 6) NOT NULL,
            low        NUMERIC(18, 6) NOT NULL,
            close      NUMERIC(18, 6) NOT NULL,
            volume     BIGINT,
            PRIMARY KEY (symbol, timeframe, ts)
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS cam_inspector_candles CASCADE;")
