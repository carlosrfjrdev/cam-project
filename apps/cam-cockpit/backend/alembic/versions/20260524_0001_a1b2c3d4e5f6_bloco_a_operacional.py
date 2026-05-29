"""bloco_a_operacional

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-24 00:01:00.000000

T-A07: Tabelas operacionais, constitucionais e habilitação do TimescaleDB.

Tabelas criadas:
  Operacional:    cam_orders, cam_trades, cam_journal_entries,
                  cam_risk_decisions, cam_violations, cam_kill_switch_events,
                  cam_checklist_pre_market, cam_checklist_post_market
  Constitucional: cam_constitution_versions, cam_pov_versions, cam_phase_history
  Guardas:        cam_positions (posições abertas)

IMUTABILIDADE: cam_journal_entries não deve ter UPDATE/DELETE.
Enforçado no repository, não na DDL (PostgreSQL não tem DDL constraint para isso).
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Habilitar TimescaleDB (necessário antes de criar hypertables)
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # ------------------------------------------------------------------
    # cam_orders — ordens propostas (intenções de operação)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("risk_decision_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("contracts > 0", name="ck_cam_orders_contracts_positive"),
        sa.CheckConstraint(
            "direction IN ('LONG', 'SHORT')",
            name="ck_cam_orders_direction",
        ),
        sa.CheckConstraint(
            "asset IN ('WIN', 'WDO')",
            name="ck_cam_orders_asset",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'EXECUTED')",
            name="ck_cam_orders_status",
        ),
    )

    # ------------------------------------------------------------------
    # cam_positions — posições abertas (controle de exposure)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_positions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("entry_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("order_id", UUID(as_uuid=True), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('OPEN', 'CLOSED', 'PARTIALLY_CLOSED')",
            name="ck_cam_positions_status",
        ),
    )

    # ------------------------------------------------------------------
    # cam_trades — execuções reais vindas do Profit
    # ------------------------------------------------------------------
    op.create_table(
        "cam_trades",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_id", UUID(as_uuid=True), nullable=True),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("entry_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("exit_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("result_gross", sa.Numeric(12, 2), nullable=True),
        sa.Column("result_net", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax_provisioned", sa.Numeric(12, 2), nullable=True),
        sa.Column("strategy", sa.String(100), nullable=True),
        sa.Column("setup", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_journal_entries — registro imutável (Art. 31)
    # IMUTÁVEL: sem UPDATE/DELETE no repository
    # ------------------------------------------------------------------
    op.create_table(
        "cam_journal_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("trade_id", UUID(as_uuid=True), nullable=True),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("entry_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("exit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("result_gross", sa.Numeric(12, 2), nullable=False),
        sa.Column("costs", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("result_net", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_provisioned", sa.Numeric(12, 2), nullable=False),
        sa.Column("strategy", sa.String(100), nullable=True),
        sa.Column("setup", sa.String(100), nullable=True),
        # A+, A, B, C — aderência às regras operacionais
        sa.Column("adherence", sa.String(10), nullable=True),
        sa.Column("emotional_note", sa.Text, nullable=True),
        sa.Column("lesson", sa.Text, nullable=True),
        # 'MANUAL', 'CSV_IMPORT', 'NTSL_CALLBACK'
        sa.Column("source", sa.String(50), nullable=False, server_default=sa.text("'MANUAL'")),
        # corrected_entry_id = None -> original; != None -> é correção de outra entry
        sa.Column("corrected_entry_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "source IN ('MANUAL', 'CSV_IMPORT', 'NTSL_CALLBACK')",
            name="ck_cam_journal_source",
        ),
    )
    op.create_index(
        "ix_cam_journal_entries_created_at",
        "cam_journal_entries",
        ["created_at"],
    )

    # ------------------------------------------------------------------
    # cam_risk_decisions — TODA decisão do Risk Engine (audit trail imutável)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_risk_decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_candidate", JSONB, nullable=False),
        sa.Column("risk_context", JSONB, nullable=False),
        # 'APPROVED' ou 'REJECTED'
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("validator", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "decision IN ('APPROVED', 'REJECTED')",
            name="ck_cam_risk_decisions_decision",
        ),
    )
    op.create_index(
        "ix_cam_risk_decisions_created_at",
        "cam_risk_decisions",
        ["created_at"],
    )

    # ------------------------------------------------------------------
    # cam_violations — violações registradas (Art. 29)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_violations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("rule", sa.String(100), nullable=False),
        sa.Column("context", JSONB, nullable=True),
        sa.Column("journal_entry_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_kill_switch_events — Art. 18: ativações/desativações
    # ------------------------------------------------------------------
    op.create_table(
        "cam_kill_switch_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "action IN ('ACTIVATE', 'DEACTIVATE')",
            name="ck_cam_kill_switch_action",
        ),
    )

    # ------------------------------------------------------------------
    # cam_checklist_pre_market — Art. 32
    # ------------------------------------------------------------------
    op.create_table(
        "cam_checklist_pre_market",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.Date, nullable=False, unique=True),
        sa.Column("items", JSONB, nullable=False),
        sa.Column("completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_checklist_post_market — Art. 33
    # ------------------------------------------------------------------
    op.create_table(
        "cam_checklist_post_market",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.Date, nullable=False, unique=True),
        sa.Column("items", JSONB, nullable=False),
        sa.Column("completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("result_summary", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_constitution_versions — Art. 38: emendas constitucionais
    # ------------------------------------------------------------------
    op.create_table(
        "cam_constitution_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_pov_versions — Art. 37: versões da POV (Playbook Operacional Vivo)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_pov_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_phase_history — transições de fase do CaM
    # ------------------------------------------------------------------
    op.create_table(
        "cam_phase_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("exited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("cam_phase_history")
    op.drop_table("cam_pov_versions")
    op.drop_table("cam_constitution_versions")
    op.drop_table("cam_checklist_post_market")
    op.drop_table("cam_checklist_pre_market")
    op.drop_table("cam_kill_switch_events")
    op.drop_table("cam_violations")
    op.drop_table("cam_risk_decisions")
    op.drop_table("cam_journal_entries")
    op.drop_table("cam_trades")
    op.drop_table("cam_positions")
    op.drop_table("cam_orders")
