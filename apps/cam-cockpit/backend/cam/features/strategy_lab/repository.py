"""
Repository do StrategyLab — escreve em strategy_* e LÊ barras de research_bars.

SQL explícito via `text()` (mesmo padrão da Research Lane — slice leve, sem ORM).
NÃO escreve em tabelas live; reusa `research_bars` como fonte de dado já ingerida
(não re-ingere — R-01/reuso). Funções assíncronas sobre AsyncSession.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.research_kernel.bars import Bar

# --------------------------------------------------------------------------- #
# Leitura de barras (research_bars, price_series='raw')
# --------------------------------------------------------------------------- #
_SELECT_BARS = text(
    """
    SELECT symbol, timeframe, ts_open, ts_close, session_date,
           open, high, low, close, volume, financial, trades, vwap, is_partial
    FROM research_bars
    WHERE symbol = :symbol AND timeframe = :timeframe AND price_series = 'raw'
      AND (:w_start IS NULL OR ts_open >= :w_start)
      AND (:w_end   IS NULL OR ts_open <  :w_end)
    ORDER BY ts_open ASC
    """
)


async def load_bars(
    session: AsyncSession,
    symbol: str,
    timeframe: str,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> list[Bar]:
    """Carrega barras canônicas de research_bars como `Bar` (ordem cronológica)."""
    res = await session.execute(
        _SELECT_BARS,
        {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "w_start": window_start,
            "w_end": window_end,
        },
    )
    bars: list[Bar] = []
    for r in res.fetchall():
        m = r._mapping
        bars.append(
            Bar(
                symbol=m["symbol"],
                timeframe=m["timeframe"],
                ts_open=m["ts_open"],
                ts_close=m["ts_close"] or m["ts_open"],
                session_date=str(m["session_date"]),
                open=float(m["open"]),
                high=float(m["high"]),
                low=float(m["low"]),
                close=float(m["close"]),
                volume=int(m["volume"] or 0),
                trades=int(m["trades"] or 0),
                financial=float(m["financial"] or 0.0),
                vwap=(float(m["vwap"]) if m["vwap"] is not None else None),
                is_partial=bool(m["is_partial"]),
            )
        )
    return bars


async def symbol_has_data(
    session: AsyncSession, symbol: str, timeframe: str
) -> int:
    """Nº de barras disponíveis (guard de proveniência — T-007)."""
    res = await session.execute(
        text(
            "SELECT count(*) FROM research_bars "
            "WHERE symbol = :s AND timeframe = :tf AND price_series = 'raw'"
        ),
        {"s": symbol.upper(), "tf": timeframe},
    )
    return int(res.scalar_one())


# --------------------------------------------------------------------------- #
# Param sets (manual | suggested)
# --------------------------------------------------------------------------- #
_INSERT_PARAM_SET = text(
    """
    INSERT INTO strategy_param_set (strategy_id, params, origin, optimization_id)
    VALUES (:strategy_id, CAST(:params AS JSONB), :origin, :optimization_id)
    RETURNING id
    """
)


async def create_param_set(
    session: AsyncSession,
    strategy_id: str,
    params_json: str,
    origin: str = "manual",
    optimization_id: int | None = None,
) -> int:
    res = await session.execute(
        _INSERT_PARAM_SET,
        {
            "strategy_id": strategy_id.upper(),
            "params": params_json,
            "origin": origin,
            "optimization_id": optimization_id,
        },
    )
    return int(res.scalar_one())


async def list_param_sets(
    session: AsyncSession, strategy_id: str
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            "SELECT id, strategy_id, params, origin, optimization_id, created_at "
            "FROM strategy_param_set WHERE strategy_id = :s "
            "ORDER BY created_at DESC LIMIT 100"
        ),
        {"s": strategy_id.upper()},
    )
    return [dict(r._mapping) for r in res.fetchall()]


# --------------------------------------------------------------------------- #
# Backtest runs + ledger de pernas
# --------------------------------------------------------------------------- #
_INSERT_RUN = text(
    """
    INSERT INTO strategy_backtest_run
        (strategy_id, param_set_id, symbols, unit, timeframe,
         window_start, window_end, mode, metrics, status)
    VALUES (:strategy_id, :param_set_id, :symbols, :unit, :timeframe,
            :window_start, :window_end, 'gross', CAST(:metrics AS JSONB), :status)
    RETURNING id
    """
)

_INSERT_LEG = text(
    """
    INSERT INTO strategy_leg_trade
        (run_id, pair_id, leg, symbol, ts_entry, price_entry, ts_exit,
         price_exit, qty, exit_reason, pnl_bruto, volume_financeiro)
    VALUES (:run_id, :pair_id, :leg, :symbol, :ts_entry, :price_entry, :ts_exit,
            :price_exit, :qty, :exit_reason, :pnl_bruto, :volume_financeiro)
    """
)


async def create_run(
    session: AsyncSession,
    strategy_id: str,
    symbols: list[str],
    unit: str,
    timeframe: str,
    metrics_json: str,
    param_set_id: int | None = None,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    status: str = "done",
) -> int:
    res = await session.execute(
        _INSERT_RUN,
        {
            "strategy_id": strategy_id.upper(),
            "param_set_id": param_set_id,
            "symbols": symbols,
            "unit": unit,
            "timeframe": timeframe,
            "window_start": window_start,
            "window_end": window_end,
            "metrics": metrics_json,
            "status": status,
        },
    )
    return int(res.scalar_one())


async def insert_legs(
    session: AsyncSession, rows: list[dict[str, Any]]
) -> int:
    if not rows:
        return 0
    await session.execute(_INSERT_LEG, rows)
    return len(rows)


async def get_run(session: AsyncSession, run_id: int) -> dict[str, Any] | None:
    res = await session.execute(
        text("SELECT * FROM strategy_backtest_run WHERE id = :id"), {"id": run_id}
    )
    row = res.fetchone()
    return dict(row._mapping) if row else None


async def get_run_legs(
    session: AsyncSession, run_id: int
) -> list[dict[str, Any]]:
    res = await session.execute(
        text(
            "SELECT pair_id, leg, symbol, ts_entry, price_entry, ts_exit, "
            "price_exit, qty, exit_reason, pnl_bruto, volume_financeiro "
            "FROM strategy_leg_trade WHERE run_id = :id "
            "ORDER BY pair_id, ts_entry"
        ),
        {"id": run_id},
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def list_runs(
    session: AsyncSession, strategy_id: str | None = None
) -> list[dict[str, Any]]:
    if strategy_id:
        res = await session.execute(
            text(
                "SELECT id, strategy_id, symbols, unit, timeframe, mode, "
                "metrics, status, created_at FROM strategy_backtest_run "
                "WHERE strategy_id = :s ORDER BY created_at DESC LIMIT 100"
            ),
            {"s": strategy_id.upper()},
        )
    else:
        res = await session.execute(
            text(
                "SELECT id, strategy_id, symbols, unit, timeframe, mode, "
                "metrics, status, created_at FROM strategy_backtest_run "
                "ORDER BY created_at DESC LIMIT 100"
            )
        )
    return [dict(r._mapping) for r in res.fetchall()]
