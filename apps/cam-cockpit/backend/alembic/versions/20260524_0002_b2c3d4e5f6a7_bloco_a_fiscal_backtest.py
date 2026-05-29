"""bloco_a_fiscal_backtest

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24 00:02:00.000000

T-A08: Tabelas fiscal, patrimonial e backtest.

Tabelas criadas:
  Fiscal:     cam_fiscal_apuration, cam_darf_history, cam_loss_compensation_ledger
  Patrimonial: cam_bucket_transactions, cam_harvest_history
  Backtest:   cam_backtest_runs, cam_backtest_trades, cam_backtest_equity_curve,
              cam_pattern_studies
  Extra:      cam_paper_trades, cam_ai_analysis
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # cam_fiscal_apuration — apuração mensal de IR
    # ------------------------------------------------------------------
    op.create_table(
        "cam_fiscal_apuration",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # date = primeiro dia do mês apurado (UNIQUE por mês)
        sa.Column("month", sa.Date, nullable=False, unique=True),
        sa.Column("gross_result", sa.Numeric(12, 2), nullable=False),
        sa.Column("costs", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("net_result", sa.Numeric(12, 2), nullable=False),
        # Alíquota IR Day Trade (20%)
        sa.Column("tax_rate", sa.Numeric(6, 4), nullable=False,
                  server_default="0.2000"),
        sa.Column("tax_due", sa.Numeric(12, 2), nullable=False),
        # IRRF retido na fonte (1% sobre lucro bruto Day Trade)
        sa.Column("irrf_retained", sa.Numeric(12, 2), nullable=False,
                  server_default="0"),
        # Prejuízo compensado neste mês (Art. 27)
        sa.Column("loss_compensation_used", sa.Numeric(12, 2), nullable=False,
                  server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_darf_history — DARFs gerados e seu ciclo de vida
    # ------------------------------------------------------------------
    op.create_table(
        "cam_darf_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("apuration_id", UUID(as_uuid=True), nullable=False),
        # competencia = mês de referência (mesmo valor de cam_fiscal_apuration.month)
        sa.Column("competencia", sa.Date, nullable=False),
        sa.Column("value", sa.Numeric(12, 2), nullable=False),
        # Vencimento: último dia útil do mês seguinte (Art. 26)
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["apuration_id"], ["cam_fiscal_apuration.id"]),
        sa.CheckConstraint(
            "status IN ('PENDING', 'PAID', 'OVERDUE')",
            name="ck_cam_darf_status",
        ),
    )

    # ------------------------------------------------------------------
    # cam_loss_compensation_ledger — prejuízos acumulados compensáveis (Art. 27)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_loss_compensation_ledger",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # Mês ao qual o prejuízo se refere
        sa.Column("month", sa.Date, nullable=False),
        sa.Column("loss_amount", sa.Numeric(12, 2), nullable=False),
        # Saldo acumulado após este lançamento
        sa.Column("accumulated_loss", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_bucket_transactions — movimentações dos 3 buckets (Art. 21)
    # Buckets: DERIVATIVO, BUFFER, CARTEIRA_HARD
    # ------------------------------------------------------------------
    op.create_table(
        "cam_bucket_transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("bucket", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("direction", sa.String(5), nullable=False),
        sa.Column("reason", sa.String(200), nullable=True),
        sa.Column("reference_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "bucket IN ('DERIVATIVO', 'BUFFER', 'CARTEIRA_HARD')",
            name="ck_cam_bucket_transactions_bucket",
        ),
        sa.CheckConstraint(
            "direction IN ('IN', 'OUT')",
            name="ck_cam_bucket_transactions_direction",
        ),
    )

    # ------------------------------------------------------------------
    # cam_harvest_history — execuções da Harvest Rule (Art. 21)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_harvest_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # Mês de referência do harvest
        sa.Column("month", sa.Date, nullable=False),
        sa.Column("net_profit", sa.Numeric(12, 2), nullable=False),
        sa.Column("carteira_hard_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("buffer_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("sangria_amount", sa.Numeric(12, 2), nullable=False,
                  server_default="0"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_backtest_runs — metadata de cada execução de backtest
    # ------------------------------------------------------------------
    op.create_table(
        "cam_backtest_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("strategy", sa.String(100), nullable=False),
        sa.Column("date_from", sa.Date, nullable=False),
        sa.Column("date_to", sa.Date, nullable=False),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("config", JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'PENDING'")),
        # Métricas calculadas após conclusão
        sa.Column("metrics", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_cam_backtest_runs_status",
        ),
    )

    # ------------------------------------------------------------------
    # cam_backtest_trades — trades simulados por run
    # ------------------------------------------------------------------
    op.create_table(
        "cam_backtest_trades",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", UUID(as_uuid=True), nullable=False),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("entry_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("exit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("result_gross", sa.Numeric(12, 2), nullable=False),
        sa.Column("costs", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("result_net", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_provisioned", sa.Numeric(12, 2), nullable=False),
        # 'APPROVED' ou 'REJECTED' — backtest sem Risk Engine é proibido (CA7.5)
        sa.Column("risk_decision", sa.String(20), nullable=False),
        sa.Column("risk_rejection_reason", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["run_id"], ["cam_backtest_runs.id"],
                                ondelete="CASCADE"),
    )
    op.create_index(
        "ix_cam_backtest_trades_run_id",
        "cam_backtest_trades",
        ["run_id"],
    )

    # ------------------------------------------------------------------
    # cam_backtest_equity_curve — curva de capital do backtest
    # ------------------------------------------------------------------
    op.create_table(
        "cam_backtest_equity_curve",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("run_id", UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("equity", sa.Numeric(12, 2), nullable=False),
        sa.Column("drawdown", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["run_id"], ["cam_backtest_runs.id"],
                                ondelete="CASCADE"),
    )
    op.create_index(
        "ix_cam_backtest_equity_run_timestamp",
        "cam_backtest_equity_curve",
        ["run_id", "timestamp"],
    )

    # ------------------------------------------------------------------
    # cam_pattern_studies — estudos de padrão de price action
    # ------------------------------------------------------------------
    op.create_table(
        "cam_pattern_studies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("config", JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_paper_trades — trades simulados em paper trading (Art. 5 CA5.5)
    # Tabela separada de cam_trades para nunca confundir com live
    # ------------------------------------------------------------------
    op.create_table(
        "cam_paper_trades",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("asset", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("contracts", sa.Integer, nullable=False),
        sa.Column("entry_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("exit_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("result_gross", sa.Numeric(12, 2), nullable=True),
        sa.Column("result_net", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax_provisioned", sa.Numeric(12, 2), nullable=True),
        sa.Column("risk_decision", sa.String(20), nullable=False),
        sa.Column("risk_rejection_reason", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    # ------------------------------------------------------------------
    # cam_ai_analysis — análises pós-mercado da IA auditora (Arts. 34-36)
    # ------------------------------------------------------------------
    op.create_table(
        "cam_ai_analysis",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        # Data do pregão analisado
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("analysis_text", sa.Text, nullable=False),
        # True = análise foi descartada por conteúdo proibido (CA8.2)
        sa.Column("has_prohibited_content", sa.Boolean, nullable=False,
                  server_default="false"),
        sa.Column("sent_telegram", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "provider IN ('ollama', 'anthropic')",
            name="ck_cam_ai_analysis_provider",
        ),
    )


def downgrade() -> None:
    op.drop_table("cam_ai_analysis")
    op.drop_table("cam_paper_trades")
    op.drop_table("cam_pattern_studies")
    op.drop_table("cam_backtest_equity_curve")
    op.drop_table("cam_backtest_trades")
    op.drop_table("cam_backtest_runs")
    op.drop_table("cam_harvest_history")
    op.drop_table("cam_bucket_transactions")
    op.drop_table("cam_loss_compensation_ledger")
    op.drop_table("cam_darf_history")
    op.drop_table("cam_fiscal_apuration")
