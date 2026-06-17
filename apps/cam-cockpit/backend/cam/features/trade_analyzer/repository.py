"""
Persistência das análises do Trade Analyzer (tabela cam_trade_analysis).

Guarda o arquivo de report (bytea) + o resultado (métricas/narrativa/ticks) para
o submenu de históricos. SQL cru via async_session_factory (padrão do projeto).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from cam._shared.infra import async_session_factory

_INSERT = text(
    """
    INSERT INTO cam_trade_analysis (
        provider, model, symbol, report_filename, report_content,
        metrics, tick_summary, tick_status, narrative,
        total_trades, gross_result, win_rate, profit_factor
    ) VALUES (
        :provider, :model, :symbol, :report_filename, :report_content,
        CAST(:metrics AS JSONB), CAST(:tick_summary AS JSONB), :tick_status, :narrative,
        :total_trades, :gross_result, :win_rate, :profit_factor
    )
    RETURNING id, created_at
    """
)

_LIST = text(
    """
    SELECT id, created_at, provider, model, symbol, report_filename,
           total_trades, gross_result, win_rate, profit_factor
    FROM cam_trade_analysis
    ORDER BY created_at DESC
    LIMIT :limit OFFSET :offset
    """
)

_GET = text(
    """
    SELECT id, created_at, provider, model, symbol, report_filename,
           metrics, tick_summary, tick_status, narrative,
           total_trades, gross_result, win_rate, profit_factor
    FROM cam_trade_analysis WHERE id = :id
    """
)

_GET_REPORT = text(
    "SELECT report_filename, report_content FROM cam_trade_analysis WHERE id = :id"
)


async def save_analysis(
    *,
    provider: str,
    model: str,
    symbol: str | None,
    report_filename: str,
    report_content: bytes,
    metrics: dict,
    tick_summary: dict | None,
    tick_status: str,
    narrative: str,
) -> dict:
    params = {
        "provider": provider,
        "model": model,
        "symbol": symbol,
        "report_filename": report_filename,
        "report_content": report_content,
        "metrics": json.dumps(metrics, ensure_ascii=False),
        "tick_summary": json.dumps(tick_summary, ensure_ascii=False)
        if tick_summary is not None
        else None,
        "tick_status": tick_status,
        "narrative": narrative,
        "total_trades": metrics.get("total_trades"),
        "gross_result": metrics.get("gross_result"),
        "win_rate": metrics.get("win_rate"),
        "profit_factor": metrics.get("profit_factor"),
    }
    async with async_session_factory() as session:
        row = (await session.execute(_INSERT, params)).first()
        await session.commit()
    return {"id": row[0], "created_at": row[1].isoformat() if row[1] else None}


async def list_analyses(limit: int = 100, offset: int = 0) -> list[dict]:
    async with async_session_factory() as session:
        rows = (
            await session.execute(_LIST, {"limit": limit, "offset": offset})
        ).mappings().all()
    return [_serialize_list(dict(r)) for r in rows]


async def get_analysis(analysis_id: int) -> dict | None:
    async with async_session_factory() as session:
        row = (await session.execute(_GET, {"id": analysis_id})).mappings().first()
    return _serialize_full(dict(row)) if row else None


async def get_report(analysis_id: int) -> tuple[str, bytes] | None:
    async with async_session_factory() as session:
        row = (await session.execute(_GET_REPORT, {"id": analysis_id})).first()
    if not row:
        return None
    content = row[1]
    return row[0], bytes(content) if content is not None else b""


def _coerce_common(d: dict[str, Any]) -> dict[str, Any]:
    if d.get("created_at") is not None:
        d["created_at"] = d["created_at"].isoformat()
    for k in ("gross_result", "win_rate", "profit_factor"):
        if d.get(k) is not None:
            d[k] = float(d[k])
    return d


def _serialize_list(d: dict[str, Any]) -> dict[str, Any]:
    return _coerce_common(d)


def _serialize_full(d: dict[str, Any]) -> dict[str, Any]:
    return _coerce_common(d)
