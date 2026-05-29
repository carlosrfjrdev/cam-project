"""bl_a_strategy_lifecycle

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-27 22:50:00.000000

TASK-002 + TASK-003 (SPEC v0.4-VISION-EVOLUTION, BL-A).

Tabelas criadas:
  cam_strategies         — registry de estratégias (N registradas, 1 ativa default)
  cam_evidence_packs     — evidências de promoção (R1.02, R1.03)

INVARIANTES:
- `cam_strategies`: unique partial index garante apenas 1 linha com is_active=true.
  Constraint constitucional: enquanto MULTI_STRATEGY_ENABLED=false (default),
  o banco impede ativar 2+ estratégias simultaneamente (defesa em profundidade).
  Quando BL-H1 ativar MULTI_STRATEGY_ENABLED=true (T046), este índice será relaxado
  via migration futura.

- `cam_evidence_packs`: imutável após inserção (sem UPDATE/DELETE no repository).
  Cada pack carrega snapshot serializado (JSONB) + hash determinístico.
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # cam_strategies — registry de estratégias
    # ------------------------------------------------------------------
    op.create_table(
        "cam_strategies",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("author", sa.String(200), nullable=False),
        sa.Column(
            "status",
            sa.String(40),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "metadata_json",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "asset IN ('WIN', 'WDO')",
            name="ck_cam_strategies_asset",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'backtested', 'walk_forward_ok', "
            "'paper_ok', 'demo_ok', 'real_authorized', 'retired')",
            name="ck_cam_strategies_status",
        ),
        sa.UniqueConstraint(
            "name", "version", name="uq_cam_strategies_name_version"
        ),
    )

    # Unique partial index — apenas 1 linha pode ter is_active=true.
    # Defesa em profundidade contra ativação simultânea de N estratégias
    # antes da emenda multiestratégia (Art. 11-A, BL-H1 T046).
    op.execute(
        "CREATE UNIQUE INDEX cam_strategies_one_active "
        "ON cam_strategies (is_active) "
        "WHERE is_active = true"
    )

    # ------------------------------------------------------------------
    # cam_evidence_packs — evidências de promoção (TASK-003)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_evidence_packs",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "strategy_id",
            UUID(as_uuid=True),
            sa.ForeignKey("cam_strategies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("status_target", sa.String(40), nullable=False),
        sa.Column("payload_json", JSONB, nullable=False),
        sa.Column("hash", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "status_target IN ('backtested', 'walk_forward_ok', "
            "'paper_ok', 'demo_ok', 'real_authorized', 'retired')",
            name="ck_cam_evidence_packs_target",
        ),
        sa.UniqueConstraint("hash", name="uq_cam_evidence_packs_hash"),
    )
    op.create_index(
        "ix_cam_evidence_packs_strategy",
        "cam_evidence_packs",
        ["strategy_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_cam_evidence_packs_strategy", table_name="cam_evidence_packs")
    op.drop_table("cam_evidence_packs")
    op.execute("DROP INDEX IF EXISTS cam_strategies_one_active")
    op.drop_table("cam_strategies")
