"""bl_g_ai_provider_calls

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-05-27 23:59:00.000000

TASK-041 (BL-G) — cam_ai_provider_calls (governança remoto AI).
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "cam_ai_provider_calls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("prompt_hash", sa.String(128), nullable=False),
        sa.Column("response_hash", sa.String(128), nullable=False),
        sa.Column("anonymized", sa.Boolean, nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "provider IN ('anthropic', 'ollama', 'openai')",
            name="ck_ai_provider_calls_provider",
        ),
    )
    op.create_index(
        "ix_ai_provider_calls_provider_ts",
        "cam_ai_provider_calls",
        ["provider", "ts"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_provider_calls_provider_ts", table_name="cam_ai_provider_calls")
    op.drop_table("cam_ai_provider_calls")
