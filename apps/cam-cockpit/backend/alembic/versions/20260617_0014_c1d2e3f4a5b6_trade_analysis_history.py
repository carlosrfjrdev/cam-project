"""Trade Analyzer — histórico de análises persistidas

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-06-17

Guarda cada análise do Trade Analyzer: o arquivo de report enviado (bytea) + o
resultado (métricas, narrativa da IA, resumo de ticks). Alimenta o submenu de
históricos.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: str | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS cam_trade_analysis (
            id              BIGSERIAL PRIMARY KEY,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            provider        TEXT NOT NULL,
            model           TEXT NOT NULL,
            symbol          TEXT,
            report_filename TEXT NOT NULL,
            report_content  BYTEA NOT NULL,
            metrics         JSONB NOT NULL,
            tick_summary    JSONB,
            tick_status     TEXT,
            narrative       TEXT NOT NULL,
            -- denormalizado para a listagem
            total_trades    INTEGER,
            gross_result    NUMERIC(18,2),
            win_rate        NUMERIC(6,2),
            profit_factor   NUMERIC(8,2)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_cam_trade_analysis_created "
        "ON cam_trade_analysis (created_at DESC);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS cam_trade_analysis CASCADE;")
