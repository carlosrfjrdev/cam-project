"""bl_b_provenance_instruments

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-27 23:00:00.000000

TASK-011 (SPEC v0.4-VISION-EVOLUTION, BL-B).

Tabelas criadas:
  cam_market_data_provenance — provenance de cada lote de ingestão (R2.01)
  cam_instruments            — Instrument Catalog (R2.05)

cam_instruments é pré-populado com WIN/WDO/IND/DOL.
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | None = "d4e5f6a7b8c9"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # cam_market_data_provenance — registro de cada lote ingerido
    # ------------------------------------------------------------------
    op.create_table(
        "cam_market_data_provenance",
        sa.Column(
            "import_id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("source", sa.String(60), nullable=False),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("asset", sa.String(20), nullable=False),
        sa.Column("ts_origin_min", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ts_origin_max", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "ts_ingestion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("tick_count", sa.BigInteger, nullable=False),
        sa.Column("hash", sa.String(128), nullable=False, unique=True),
        sa.Column(
            "quality_flags",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "license_terms_ack",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(
        "ix_cam_market_data_provenance_asset",
        "cam_market_data_provenance",
        ["asset", "ts_origin_min"],
    )

    # ------------------------------------------------------------------
    # cam_instruments — Instrument Catalog
    # ------------------------------------------------------------------
    op.create_table(
        "cam_instruments",
        sa.Column("ticker", sa.String(20), primary_key=True),
        sa.Column("asset_class", sa.String(20), nullable=False),
        sa.Column(
            "exchange", sa.String(20), nullable=False, server_default="B3"
        ),
        sa.Column("contract_size", sa.Numeric(12, 4), nullable=False),
        sa.Column("tick_size", sa.Numeric(12, 4), nullable=False),
        sa.Column("point_value", sa.Numeric(12, 4), nullable=False),
        sa.Column(
            "active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.CheckConstraint(
            "asset_class IN ('futures', 'equity', 'fii', 'etf', 'other')",
            name="ck_cam_instruments_asset_class",
        ),
    )

    # Seed canônico (R2.05) — WIN/WDO ativos por default; IND/DOL inativos.
    op.execute(
        """
        INSERT INTO cam_instruments (ticker, asset_class, exchange, contract_size,
                                     tick_size, point_value, active)
        VALUES
            ('WIN', 'futures', 'B3', 1, 5, 0.20, true),
            ('WDO', 'futures', 'B3', 1, 0.5, 10.00, true),
            ('IND', 'futures', 'B3', 1, 5, 1.00, false),
            ('DOL', 'futures', 'B3', 1, 0.5, 50.00, false);
        """
    )


def downgrade() -> None:
    op.drop_table("cam_instruments")
    op.drop_index(
        "ix_cam_market_data_provenance_asset",
        table_name="cam_market_data_provenance",
    )
    op.drop_table("cam_market_data_provenance")
