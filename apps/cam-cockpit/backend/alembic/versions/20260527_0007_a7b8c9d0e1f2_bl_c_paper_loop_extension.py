"""bl_c_paper_loop_extension

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-27 23:30:00.000000

TASK-015 (BL-C) — Estende cam_paper_trades com campos do loop governado
(strategy_id, intent_id, adherence, ts_open, ts_close, costs, ir_provisioned).
Adiciona cam_strategy_runtime_state usado em T017/T048.
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f6a7b8c9d0e1"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # Extende cam_paper_trades — colunas faltantes para BL-C
    op.add_column(
        "cam_paper_trades",
        sa.Column("strategy_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("intent_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("adherence", sa.Numeric(5, 4), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("ts_open", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("ts_close", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("costs", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column(
        "cam_paper_trades",
        sa.Column("ir_provisioned", sa.Numeric(12, 2), nullable=True),
    )
    op.create_index(
        "ix_cam_paper_trades_strategy",
        "cam_paper_trades",
        ["strategy_id", "ts_open"],
    )

    # Runtime state — gain lock individual (T048), suspensões, kill switch
    op.create_table(
        "cam_strategy_runtime_state",
        sa.Column(
            "strategy_id",
            UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "is_suspended",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "suspended_until_ts",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("suspension_reason", sa.Text, nullable=True),
        sa.Column(
            "daily_pnl_pct",
            sa.Numeric(8, 6),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("cam_strategy_runtime_state")
    op.drop_index("ix_cam_paper_trades_strategy", table_name="cam_paper_trades")
    op.drop_column("cam_paper_trades", "ir_provisioned")
    op.drop_column("cam_paper_trades", "costs")
    op.drop_column("cam_paper_trades", "ts_close")
    op.drop_column("cam_paper_trades", "ts_open")
    op.drop_column("cam_paper_trades", "adherence")
    op.drop_column("cam_paper_trades", "intent_id")
    op.drop_column("cam_paper_trades", "strategy_id")
