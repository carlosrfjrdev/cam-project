"""Research Lane R0 — schema research_* (Lead-Lag v0.5.1)

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-06-03

SPEC v0.5 (ADR-015) — Research Lane ISOLADA do live. Schema research_* próprio:
barras canônicas (M1 + derivadas), ticks com agressor (flags), provenance,
snapshots imutáveis com hash, runs, resultados, quality checks, calendário B3.

NÃO reusa cam_candles_* do live (faltam provenance/calendário/snapshot/hash —
ADR-015 decisão 1). research_ticks é hypertable (tick é volumoso).
"""
from collections.abc import Sequence

from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: str | None = "e1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---- provenance por lote ingerido (R-03) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_data_sources (
            id              BIGSERIAL PRIMARY KEY,
            bar_origin      TEXT NOT NULL,          -- broker_ohlcv | tick | ...
            ts_source       TEXT NOT NULL,          -- exchange | broker_recv | local_ingest
            aggressor_source TEXT,                  -- exchange | broker | lee_ready | unknown
            symbol          TEXT NOT NULL,
            source_timeframe TEXT,
            window_start    TIMESTAMPTZ,
            window_end      TIMESTAMPTZ,
            ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
            raw_batch_hash  TEXT NOT NULL
        );
        """
    )

    # ---- regra de agregacao versionavel (R-10/R-12) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_aggregation_rules (
            id              BIGSERIAL PRIMARY KEY,
            rule_name       TEXT NOT NULL,
            anchor          TEXT NOT NULL DEFAULT 'session_open',
            partial_handling TEXT NOT NULL DEFAULT 'flag_is_partial',
            vwap_method     TEXT NOT NULL DEFAULT 'recompute_from_m1',
            definition_hash TEXT NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (definition_hash)
        );
        """
    )

    # ---- calendario B3 versionado (R-13) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_calendar (
            session_date    DATE NOT NULL,
            calendar_version TEXT NOT NULL,
            is_trading_day  BOOLEAN NOT NULL DEFAULT TRUE,
            session_open    TIME,
            session_close   TIME,
            early_close     BOOLEAN NOT NULL DEFAULT FALSE,
            PRIMARY KEY (session_date, calendar_version)
        );
        """
    )

    # ---- barras canonicas: timeframe e COLUNA, nao tabela por TF (R-09) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_bars (
            symbol          TEXT NOT NULL,
            timeframe       TEXT NOT NULL,
            ts_open         TIMESTAMPTZ NOT NULL,
            ts_close        TIMESTAMPTZ,
            session_date    DATE,
            open            NUMERIC(18,6) NOT NULL,
            high            NUMERIC(18,6) NOT NULL,
            low             NUMERIC(18,6) NOT NULL,
            close           NUMERIC(18,6) NOT NULL,
            volume          BIGINT,
            financial       NUMERIC(20,2),
            trades          BIGINT,
            vwap            NUMERIC(18,6),
            is_partial      BOOLEAN NOT NULL DEFAULT FALSE,
            price_series    TEXT NOT NULL DEFAULT 'raw',  -- raw | adjusted
            provenance_id   BIGINT REFERENCES research_data_sources(id),
            aggregation_rule_id BIGINT REFERENCES research_aggregation_rules(id),
            PRIMARY KEY (symbol, timeframe, price_series, ts_open)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_research_bars_sym_tf_date "
        "ON research_bars (symbol, timeframe, session_date);"
    )

    # ---- ticks com agressor: event-time, hypertable (R-06/R-07) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_ticks (
            symbol          TEXT NOT NULL,
            t_msc           BIGINT NOT NULL,         -- timestamp em milissegundos
            ts              TIMESTAMPTZ NOT NULL,    -- coluna de particao da hypertable
            price           NUMERIC(18,6) NOT NULL,
            volume          BIGINT,
            aggressor       SMALLINT NOT NULL DEFAULT 0,  -- +1 comprador, -1 vendedor, 0 indef
            flags_raw       INTEGER NOT NULL DEFAULT 0,
            provenance_id   BIGINT REFERENCES research_data_sources(id)
        );
        """
    )
    op.execute(
        """
        SELECT create_hypertable(
            'research_ticks', 'ts',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_research_ticks_sym_ts "
        "ON research_ticks (symbol, ts);"
    )

    # ---- snapshot imutavel com hash composto (R-16) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_dataset_snapshots (
            id              BIGSERIAL PRIMARY KEY,
            symbols         TEXT[] NOT NULL,
            timeframes_included TEXT[] NOT NULL,
            mode            TEXT NOT NULL DEFAULT 'both',  -- intraday | swing | both
            window_start    TIMESTAMPTZ,
            window_end      TIMESTAMPTZ,
            composite_hash  TEXT NOT NULL,
            calendar_version TEXT,
            with_ticks      BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            archived        BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
    )

    # ---- runs parametrizaveis (R-30) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_runs (
            id              BIGSERIAL PRIMARY KEY,
            snapshot_id     BIGINT REFERENCES research_dataset_snapshots(id),
            lens            TEXT,                    -- fast | slow
            mode            TEXT,                    -- intraday | swing | both
            sources         TEXT[] NOT NULL,
            target          TEXT NOT NULL,
            delta_grid      INTEGER[] NOT NULL,
            timeframes      TEXT[],
            thresholds      JSONB,
            n_trials        BIGINT NOT NULL DEFAULT 0,
            status          TEXT NOT NULL DEFAULT 'queued',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            archived        BOOLEAN NOT NULL DEFAULT FALSE
        );
        """
    )

    # ---- resultados por celula (R-20/R-25/R-30) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_run_results (
            id              BIGSERIAL PRIMARY KEY,
            run_id          BIGINT REFERENCES research_runs(id),
            source          TEXT NOT NULL,
            target          TEXT NOT NULL,
            timeframe       TEXT,
            delta_or_tau    INTEGER NOT NULL,
            correlation     DOUBLE PRECISION,
            mu_net          DOUBLE PRECISION,
            n_samples       BIGINT NOT NULL DEFAULT 0,
            dsr             DOUBLE PRECISION,
            fdr_q           DOUBLE PRECISION,
            verdict         TEXT NOT NULL DEFAULT 'OK'  -- OK | INSUFFICIENT_DATA | KILLED
        );
        """
    )

    # ---- quality checks (R-17) ----
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS research_data_quality_checks (
            id              BIGSERIAL PRIMARY KEY,
            snapshot_id     BIGINT REFERENCES research_dataset_snapshots(id),
            symbol          TEXT,
            timeframe       TEXT,
            check_name      TEXT NOT NULL,
            value           DOUBLE PRECISION,
            ts              TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )


def downgrade() -> None:
    for tbl in [
        "research_data_quality_checks",
        "research_run_results",
        "research_runs",
        "research_dataset_snapshots",
        "research_ticks",
        "research_bars",
        "research_calendar",
        "research_aggregation_rules",
        "research_data_sources",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {tbl} CASCADE;")
