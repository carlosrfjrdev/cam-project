"""StrategyLab — schema strategy_* (Onda 1, ADR-SL-02)

Revision ID: b1c2d3e4f5a6
Revises: f2a3b4c5d6e7
Create Date: 2026-06-03

Tabelas novas de DOMÍNIO de estratégia (par como unidade). Reusa research_bars/
research_ticks para dados (não recria). MVP de valores brutos: sem custo/IR.
"""
from collections.abc import Sequence

from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: str | None = "f2a3b4c5d6e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # conjuntos de parâmetros (manual | suggested) — T-004
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_param_set (
            id              BIGSERIAL PRIMARY KEY,
            strategy_id     TEXT NOT NULL,
            params          JSONB NOT NULL,
            origin          TEXT NOT NULL DEFAULT 'manual',   -- manual | suggested
            optimization_id BIGINT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_strategy_param_set_strategy "
        "ON strategy_param_set (strategy_id);"
    )

    # runs de backtest do strategy_lab (mode bruto, multi-símbolo) — T-005
    # NÃO toca features/backtest (não-regressão R-12).
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_backtest_run (
            id              BIGSERIAL PRIMARY KEY,
            strategy_id     TEXT NOT NULL,
            param_set_id    BIGINT REFERENCES strategy_param_set(id),
            symbols         TEXT[] NOT NULL,
            unit            TEXT NOT NULL DEFAULT 'single',   -- single | pair | basket
            timeframe       TEXT NOT NULL,
            window_start    TIMESTAMPTZ,
            window_end      TIMESTAMPTZ,
            mode            TEXT NOT NULL DEFAULT 'gross',     -- MVP: sempre gross
            metrics         JSONB,
            status          TEXT NOT NULL DEFAULT 'done',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )

    # ledger de trades — par como unidade (leg + pair_id) — T-006
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_leg_trade (
            id                BIGSERIAL PRIMARY KEY,
            run_id            BIGINT NOT NULL REFERENCES strategy_backtest_run(id),
            pair_id           INTEGER NOT NULL,                 -- agrupa as pernas de um trade
            leg               TEXT NOT NULL,                    -- long | short
            symbol            TEXT NOT NULL,
            ts_entry          TIMESTAMPTZ NOT NULL,
            price_entry       NUMERIC(18,6) NOT NULL,
            ts_exit           TIMESTAMPTZ NOT NULL,
            price_exit        NUMERIC(18,6) NOT NULL,
            qty               INTEGER NOT NULL,
            exit_reason       TEXT NOT NULL,                    -- stop|target|time|session|signal
            pnl_bruto         NUMERIC(18,6) NOT NULL,
            volume_financeiro NUMERIC(20,2) NOT NULL
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_strategy_leg_trade_run "
        "ON strategy_leg_trade (run_id, pair_id);"
    )


def downgrade() -> None:
    for tbl in ["strategy_leg_trade", "strategy_backtest_run", "strategy_param_set"]:
        op.execute(f"DROP TABLE IF EXISTS {tbl} CASCADE;")
