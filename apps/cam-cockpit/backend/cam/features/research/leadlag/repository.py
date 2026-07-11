"""
Repository da Research Lane — escreve APENAS em research_* (R-34, ADR-015).

Isolamento técnico: nenhuma escrita em tabelas live. SQL explícito (sem ORM
para manter o slice leve). Funções assíncronas sobre AsyncSession.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_INSERT_SOURCE = text(
    """
    INSERT INTO research_data_sources
        (bar_origin, ts_source, aggressor_source, symbol, source_timeframe,
         window_start, window_end, raw_batch_hash)
    VALUES (:bar_origin, :ts_source, :aggressor_source, :symbol, :source_tf,
            to_timestamp(:w_start), to_timestamp(:w_end), :hash)
    RETURNING id
    """
)

_INSERT_BAR = text(
    """
    INSERT INTO research_bars
        (symbol, timeframe, ts_open, ts_close, session_date, open, high, low,
         close, volume, financial, trades, vwap, is_partial, price_series,
         provenance_id)
    VALUES (:symbol, :timeframe, to_timestamp(:ts_open), to_timestamp(:ts_close),
            :session_date, :open, :high, :low, :close, :volume, :financial,
            :trades, :vwap, :is_partial, :price_series, :provenance_id)
    ON CONFLICT (symbol, timeframe, price_series, ts_open) DO UPDATE
      SET high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close,
          volume=EXCLUDED.volume, is_partial=EXCLUDED.is_partial
    """
)

_INSERT_TICK = text(
    """
    INSERT INTO research_ticks
        (symbol, t_msc, ts, price, volume, aggressor, flags_raw, provenance_id)
    VALUES (:symbol, :t_msc, to_timestamp(:ts_s), :price, :volume, :aggressor,
            :flags_raw, :provenance_id)
    """
)

_INSERT_SNAPSHOT = text(
    """
    INSERT INTO research_dataset_snapshots
        (symbols, timeframes_included, mode, composite_hash, calendar_version,
         with_ticks)
    VALUES (:symbols, :timeframes, :mode, :composite_hash, :calendar_version,
            :with_ticks)
    RETURNING id
    """
)

_INSERT_QC = text(
    """
    INSERT INTO research_data_quality_checks
        (snapshot_id, symbol, timeframe, check_name, value)
    VALUES (:snapshot_id, :symbol, :timeframe, :check_name, :value)
    """
)


async def insert_source(session: AsyncSession, **kw: Any) -> int:
    row = await session.execute(_INSERT_SOURCE, kw)
    return int(row.scalar_one())


async def insert_bars(session: AsyncSession, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    await session.execute(_INSERT_BAR, rows)
    return len(rows)


async def insert_ticks(session: AsyncSession, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    await session.execute(_INSERT_TICK, rows)
    return len(rows)


async def insert_snapshot(session: AsyncSession, **kw: Any) -> int:
    row = await session.execute(_INSERT_SNAPSHOT, kw)
    return int(row.scalar_one())


async def insert_quality_check(session: AsyncSession, **kw: Any) -> None:
    await session.execute(_INSERT_QC, kw)


_SELECT_BAR_CLOSES = text(
    """
    SELECT close
    FROM research_bars
    WHERE symbol = :symbol AND timeframe = :timeframe AND price_series = 'raw'
    ORDER BY ts_open ASC
    """
)

_SELECT_TICKS = text(
    """
    SELECT t_msc, aggressor, volume, price
    FROM research_ticks
    WHERE symbol = :symbol
    ORDER BY ts ASC
    """
)

_INSERT_RUN = text(
    """
    INSERT INTO research_runs
        (snapshot_id, lens, mode, sources, target, delta_grid, timeframes,
         n_trials, status)
    VALUES (:snapshot_id, :lens, :mode, :sources, :target, :delta_grid,
            :timeframes, :n_trials, :status)
    RETURNING id
    """
)

_INSERT_RESULT = text(
    """
    INSERT INTO research_run_results
        (run_id, source, target, timeframe, delta_or_tau, correlation, mu_net,
         n_samples, dsr, fdr_q, verdict)
    VALUES (:run_id, :source, :target, :timeframe, :delta, :correlation,
            :mu_net, :n_samples, :dsr, :fdr_q, :verdict)
    """
)

_UPDATE_RUN_STATUS = text(
    "UPDATE research_runs SET status = :status WHERE id = :run_id"
)


async def bar_closes(
    session: AsyncSession, symbol: str, timeframe: str
) -> list[float]:
    """Série de closes (ordem cronológica) de research_bars."""
    res = await session.execute(
        _SELECT_BAR_CLOSES, {"symbol": symbol.upper(), "timeframe": timeframe}
    )
    return [float(r[0]) for r in res.fetchall()]


async def ticks_signed(
    session: AsyncSession, symbol: str
) -> list[dict[str, Any]]:
    """Ticks com agressor (event-time) de research_ticks."""
    res = await session.execute(_SELECT_TICKS, {"symbol": symbol.upper()})
    return [
        {"t_msc": int(r[0]), "aggressor": int(r[1]), "volume": int(r[2] or 0)}
        for r in res.fetchall()
    ]


async def create_run(session: AsyncSession, **kw: Any) -> int:
    row = await session.execute(_INSERT_RUN, kw)
    return int(row.scalar_one())


async def insert_results(
    session: AsyncSession, rows: list[dict[str, Any]]
) -> int:
    if not rows:
        return 0
    await session.execute(_INSERT_RESULT, rows)
    return len(rows)


async def set_run_status(session: AsyncSession, run_id: int, status: str) -> None:
    await session.execute(_UPDATE_RUN_STATUS, {"run_id": run_id, "status": status})


async def get_run(session: AsyncSession, run_id: int) -> dict[str, Any] | None:
    res = await session.execute(
        text("SELECT * FROM research_runs WHERE id = :id"), {"id": run_id}
    )
    row = res.fetchone()
    return dict(row._mapping) if row else None


async def get_run_results(
    session: AsyncSession, run_id: int
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            "SELECT source, target, timeframe, delta_or_tau, correlation, "
            "mu_net, n_samples, dsr, fdr_q, verdict FROM research_run_results "
            "WHERE run_id = :id ORDER BY source, target, delta_or_tau"
        ),
        {"id": run_id},
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def list_runs(session: AsyncSession) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            "SELECT id, lens, mode, sources, target, delta_grid, n_trials, "
            "status, created_at FROM research_runs "
            "WHERE archived = FALSE ORDER BY created_at DESC LIMIT 100"
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def total_trials(session: AsyncSession) -> int:
    res = await session.execute(
        text("SELECT COALESCE(SUM(n_trials), 0) FROM research_runs")
    )
    return int(res.scalar_one())


async def purge_dataset(
    session: AsyncSession, symbol: str | None = None
) -> dict[str, int]:
    """
    Limpa o dataset (research_bars + research_ticks). Por símbolo se `symbol`
    dado; senão TODO o dataset. Mantém runs/análises (research_runs).
    """
    if symbol:
        s = symbol.upper()
        tk = await session.execute(
            text("DELETE FROM research_ticks WHERE symbol = :s"), {"s": s}
        )
        br = await session.execute(
            text("DELETE FROM research_bars WHERE symbol = :s"), {"s": s}
        )
    else:
        tk = await session.execute(text("DELETE FROM research_ticks"))
        br = await session.execute(text("DELETE FROM research_bars"))
    return {"bars": int(br.rowcount or 0), "ticks": int(tk.rowcount or 0)}


async def data_health(session: AsyncSession) -> dict[str, Any]:
    """Cobertura por símbolo/TF + liquidez de tick (R-08 / Data Health)."""
    bars = await session.execute(
        text(
            """
            SELECT symbol, timeframe, count(*) AS n,
                   min(ts_open) AS first_ts, max(ts_open) AS last_ts
            FROM research_bars
            GROUP BY symbol, timeframe
            ORDER BY symbol, timeframe
            """
        )
    )
    ticks = await session.execute(
        text(
            """
            SELECT symbol, count(*) AS n_ticks,
                   sum(CASE WHEN aggressor <> 0 THEN 1 ELSE 0 END) AS n_aggressor,
                   min(ts) AS first_ts, max(ts) AS last_ts
            FROM research_ticks
            GROUP BY symbol
            ORDER BY symbol
            """
        )
    )
    return {
        "bars": [dict(r._mapping) for r in bars],
        "ticks": [dict(r._mapping) for r in ticks],
    }
