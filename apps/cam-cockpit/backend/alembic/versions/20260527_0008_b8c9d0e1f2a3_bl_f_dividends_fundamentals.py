"""bl_f_dividends_fundamentals

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-05-27 23:45:00.000000

TASK-031 + TASK-032 (BL-F SPEC v0.4).

Tabelas criadas:
  cam_dividends_calendar    — calendário de proventos por ticker (R6.01)
  cam_dividends_received    — proventos recebidos pelo operador (R6.02)
  cam_fundamentals_snapshot — 7 indicadores R-20 (R6.03)
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # cam_dividends_calendar
    op.create_table(
        "cam_dividends_calendar",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("ex_date", sa.Date, nullable=False),
        sa.Column("payment_date", sa.Date, nullable=False),
        sa.Column("amount_per_share", sa.Numeric(16, 6), nullable=False),
        sa.Column("source", sa.String(60), nullable=False),
        sa.Column("hash", sa.String(128), nullable=False, unique=True),
        sa.CheckConstraint(
            "type IN ('DIV', 'JCP')", name="ck_div_calendar_type"
        ),
        sa.UniqueConstraint(
            "ticker", "ex_date", "type", name="uq_div_calendar_ticker_ex_type"
        ),
    )
    op.create_index(
        "ix_div_calendar_payment", "cam_dividends_calendar", ["payment_date"]
    )

    # cam_dividends_received
    op.create_table(
        "cam_dividends_received",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(16, 4), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("payment_date", sa.Date, nullable=False),
        sa.Column(
            "holding_id_ref",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "cam_carteira_hard_holdings.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.CheckConstraint(
            "type IN ('DIV', 'JCP')", name="ck_div_received_type"
        ),
    )

    # cam_fundamentals_snapshot (R-20: 7 indicadores)
    op.create_table(
        "cam_fundamentals_snapshot",
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("ts_snapshot", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(60), nullable=False),
        sa.Column("dy", sa.Numeric(8, 4), nullable=True),
        sa.Column("pl", sa.Numeric(10, 4), nullable=True),
        sa.Column("pvp", sa.Numeric(10, 4), nullable=True),
        sa.Column("roe", sa.Numeric(8, 4), nullable=True),
        sa.Column("div_liq_ebitda", sa.Numeric(10, 4), nullable=True),
        sa.Column("payout", sa.Numeric(8, 4), nullable=True),
        sa.Column("roic", sa.Numeric(8, 4), nullable=True),
        sa.Column("hash", sa.String(128), nullable=False, unique=True),
        sa.PrimaryKeyConstraint(
            "ticker", "ts_snapshot", name="pk_fundamentals_snapshot"
        ),
    )


def downgrade() -> None:
    op.drop_table("cam_fundamentals_snapshot")
    op.drop_table("cam_dividends_received")
    op.drop_index("ix_div_calendar_payment", table_name="cam_dividends_calendar")
    op.drop_table("cam_dividends_calendar")
