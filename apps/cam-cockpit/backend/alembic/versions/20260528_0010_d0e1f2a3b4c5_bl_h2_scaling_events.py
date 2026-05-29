"""bl_h2_scaling_events

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-05-28 00:15:00.000000

TASK-052 (BL-H2) — cam_constitutional_scaling_events.
Implementa registro de eventos do escalonamento (Art. 11-B).
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "cam_constitutional_scaling_events",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("strategy_id", UUID(as_uuid=True), nullable=True),
        sa.Column("proposed_limit_win", sa.Integer, nullable=True),
        sa.Column("proposed_limit_wdo", sa.Integer, nullable=True),
        sa.Column("evidence_json", JSONB, nullable=True),
        sa.Column("cooldown_days", sa.Integer, nullable=True),
        sa.Column(
            "cooldown_ends_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.CheckConstraint(
            "event_type IN ('ELIGIBILITY_COMPUTED', 'ELIGIBILITY_READY', "
            "'PROPOSED', 'APPROVED', 'REVOKED', 'IN_FORCE', "
            "'AUTO_REVERTED', 'SOFT_KILL_SWITCH', 'BLOCKED_ATTEMPT')",
            name="ck_scaling_events_event_type",
        ),
    )
    op.create_index(
        "ix_scaling_events_strategy_ts",
        "cam_constitutional_scaling_events",
        ["strategy_id", "ts"],
        postgresql_ops={"ts": "DESC"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_scaling_events_strategy_ts",
        table_name="cam_constitutional_scaling_events",
    )
    op.drop_table("cam_constitutional_scaling_events")
