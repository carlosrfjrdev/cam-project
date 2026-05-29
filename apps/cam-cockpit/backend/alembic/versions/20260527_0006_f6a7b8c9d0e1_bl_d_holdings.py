"""bl_d_holdings

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-27 23:15:00.000000

TASK-020 (BL-D) — cam_carteira_hard_holdings.
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "cam_carteira_hard_holdings",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column(
            "asset_class",
            sa.String(20),
            nullable=False,
            server_default="equity",
        ),
        sa.Column("quantity", sa.Numeric(16, 4), nullable=False),
        sa.Column("avg_price", sa.Numeric(16, 4), nullable=False),
        sa.Column(
            "first_acquisition_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "last_acquisition_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("hash", sa.String(128), nullable=False, unique=True),
        sa.CheckConstraint(
            "quantity > 0", name="ck_cam_holdings_quantity_positive"
        ),
        sa.CheckConstraint(
            "source IN ('MANUAL_UI', 'GENIAL_IMPORT')",
            name="ck_cam_holdings_source",
        ),
        sa.CheckConstraint(
            "asset_class IN ('equity', 'fii', 'etf', 'other')",
            name="ck_cam_holdings_asset_class_non_derivative",
        ),
    )
    op.create_index(
        "ix_cam_holdings_ticker",
        "cam_carteira_hard_holdings",
        ["ticker"],
    )


def downgrade() -> None:
    op.drop_index("ix_cam_holdings_ticker", table_name="cam_carteira_hard_holdings")
    op.drop_table("cam_carteira_hard_holdings")
