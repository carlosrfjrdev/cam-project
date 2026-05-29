"""bloco_a_timescaledb

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-24 00:03:00.000000

T-A09: Hypertables TimescaleDB, continuous aggregates de candles e compressão.

Hypertables:
  cam_market_ticks         — chunk 1 dia, compressão > 7 dias
  cam_market_book_snapshots — chunk 1 dia, compressão > 3 dias

Continuous aggregates (candles):
  cam_candles_1s, cam_candles_5s, cam_candles_1m, cam_candles_5m,
  cam_candles_15m, cam_candles_1h, cam_candles_1d

Nota: continuous aggregates requerem TimescaleDB com licença Apache ou TSL.
No container timescale/timescaledb:latest-pg16, todas as funcionalidades
utilizadas aqui são da licença Apache (gratuita).
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # cam_market_ticks — hypertable de ticks de mercado (WIN, WDO)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE cam_market_ticks (
            id          BIGSERIAL NOT NULL,
            asset       VARCHAR(10) NOT NULL,
            price       NUMERIC(12, 2) NOT NULL,
            volume      INTEGER NOT NULL,
            timestamp   TIMESTAMPTZ NOT NULL,
            source      VARCHAR(50)
        )
    """)

    # Converter para hypertable particionada por timestamp (chunk = 1 dia)
    op.execute("""
        SELECT create_hypertable(
            'cam_market_ticks',
            'timestamp',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        )
    """)

    op.create_index(
        "ix_cam_market_ticks_asset_timestamp",
        "cam_market_ticks",
        ["asset", "timestamp"],
    )

    # Compressão automática após 7 dias (ADR-004)
    op.execute("""
        ALTER TABLE cam_market_ticks
        SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'asset',
            timescaledb.compress_orderby = 'timestamp DESC'
        )
    """)
    op.execute("""
        SELECT add_compression_policy(
            'cam_market_ticks',
            INTERVAL '7 days',
            if_not_exists => TRUE
        )
    """)

    # ------------------------------------------------------------------
    # cam_market_book_snapshots — hypertable de book de ofertas
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE cam_market_book_snapshots (
            id        BIGSERIAL NOT NULL,
            asset     VARCHAR(10) NOT NULL,
            bids      JSONB NOT NULL,
            asks      JSONB NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL
        )
    """)

    op.execute("""
        SELECT create_hypertable(
            'cam_market_book_snapshots',
            'timestamp',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        )
    """)

    # Compressão após 3 dias (book snapshots têm ciclo de vida curto)
    op.execute("""
        ALTER TABLE cam_market_book_snapshots
        SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'asset',
            timescaledb.compress_orderby = 'timestamp DESC'
        )
    """)
    op.execute("""
        SELECT add_compression_policy(
            'cam_market_book_snapshots',
            INTERVAL '3 days',
            if_not_exists => TRUE
        )
    """)

    # ------------------------------------------------------------------
    # Continuous Aggregates — candles em múltiplos timeframes
    # Cada view é um continuous aggregate materializado e mantido em background.
    # Consultas de backtest e dashboard consultam a view (pré-agregado) em ms.
    # ------------------------------------------------------------------

    _create_candle_aggregate("cam_candles_1s", "1 second")
    _create_candle_aggregate("cam_candles_5s", "5 seconds")
    _create_candle_aggregate("cam_candles_1m", "1 minute")
    _create_candle_aggregate("cam_candles_5m", "5 minutes")
    _create_candle_aggregate("cam_candles_15m", "15 minutes")
    _create_candle_aggregate("cam_candles_1h", "1 hour")
    _create_candle_aggregate("cam_candles_1d", "1 day")


def _create_candle_aggregate(view_name: str, bucket_interval: str) -> None:
    """Cria um continuous aggregate de candles para o intervalo especificado."""
    op.execute(f"""
        CREATE MATERIALIZED VIEW {view_name}
        WITH (timescaledb.continuous) AS
        SELECT
            asset,
            time_bucket('{bucket_interval}', timestamp) AS bucket,
            first(price, timestamp)  AS open,
            max(price)               AS high,
            min(price)               AS low,
            last(price, timestamp)   AS close,
            sum(volume)              AS volume
        FROM cam_market_ticks
        GROUP BY asset, time_bucket('{bucket_interval}', timestamp)
        WITH NO DATA
    """)


def downgrade() -> None:
    # Remover continuous aggregates na ordem inversa
    for view in [
        "cam_candles_1d",
        "cam_candles_1h",
        "cam_candles_15m",
        "cam_candles_5m",
        "cam_candles_1m",
        "cam_candles_5s",
        "cam_candles_1s",
    ]:
        op.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view} CASCADE")

    op.drop_table("cam_market_book_snapshots")
    op.drop_table("cam_market_ticks")
