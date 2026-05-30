"""
Router FastAPI da feature market_data.

Endpoints:
    GET  /api/v1/market-data/status   → status do serviço de ingestão
    POST /api/v1/market-data/ingest   → ingestão de ticks via upload CSV

Fase 0: ingestão via CSV (Profit export).
Fase 1+: WebSocket / streaming em tempo real.
"""
import os
import tempfile
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session

router = APIRouter(prefix="/api/v1/market-data", tags=["market-data"])


@router.get("/status")
async def status() -> dict:
    """Status do serviço de ingestão de dados de mercado."""
    return {
        "status": "ok",
        "message": "MarketData service — ingestão de ticks disponível",
        "phase": "0",
        "supported_sources": ["CSV"],
        "upcoming_sources": ["WebSocket", "API"],
    }


@router.post("/ingest")
async def ingest_ticks(file: UploadFile = File(...)) -> dict:
    """
    Ingestão de ticks via CSV exportado do Profit.

    Parseia o CSV, valida campos e retorna contagem.
    Persistência real (TimescaleDB): pendente T-H06.

    Formato esperado:
        asset,price,volume,timestamp
    """
    from cam.features.market_data.csv_parser import TickCSVParser
    from cam.features.market_data.domain import IngestResult

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    # Salva em arquivo temporário para o parser (que espera filepath)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        parser = TickCSVParser()
        ticks = parser.parse(tmp_path)
    finally:
        os.unlink(tmp_path)

    # Stub sem banco: todos são "inseridos" na memória
    result = IngestResult(
        total_rows=len(ticks),
        inserted=len(ticks),
        skipped=0,
    )

    return {
        "total_rows": result.total_rows,
        "inserted": result.inserted,
        "skipped": result.skipped,
        "success_rate": result.success_rate,
        "message": "Ingestão sem banco — persistência pendente (T-H06)",
    }


# ---------------------------------------------------------------------------
# Provenance + Instruments — TASK-U008 (BL-UI-0). Read-only.
# ---------------------------------------------------------------------------


@router.get("/provenance")
async def provenance(
    session: AsyncSession = Depends(get_db_session),
    limit: int = 200,
) -> list[dict[str, Any]]:
    """
    Lotes ingeridos com proveniência: fonte, janela temporal, tick_count, hash,
    quality_flags (has_gaps/zero_volume/out_of_hours). Read-only.
    """
    result = await session.execute(
        sa_text(
            "SELECT import_id, source, source_url, asset, ts_origin_min, "
            "       ts_origin_max, ts_ingestion, tick_count, hash, "
            "       quality_flags, license_terms_ack "
            "FROM cam_market_data_provenance "
            "ORDER BY ts_ingestion DESC LIMIT :lim"
        ),
        {"lim": limit},
    )
    out: list[dict[str, Any]] = []
    for r in result.fetchall():
        m = dict(r._mapping)
        out.append(
            {
                "import_id": str(m["import_id"]),
                "source": m["source"],
                "source_url": m.get("source_url"),
                "asset": m["asset"],
                "ts_origin_min": m["ts_origin_min"].isoformat()
                if m.get("ts_origin_min")
                else None,
                "ts_origin_max": m["ts_origin_max"].isoformat()
                if m.get("ts_origin_max")
                else None,
                "ts_ingestion": m["ts_ingestion"].isoformat()
                if m.get("ts_ingestion")
                else None,
                "tick_count": m["tick_count"],
                "hash": m["hash"],
                "quality_flags": m.get("quality_flags") or {},
                "license_terms_ack": m["license_terms_ack"],
            }
        )
    return out


@router.get("/instruments")
async def instruments(
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, Any]]:
    """Catálogo de instrumentos (WIN/WDO com point_value). Read-only."""
    result = await session.execute(
        sa_text(
            "SELECT ticker, asset_class, exchange, contract_size, tick_size, "
            "       point_value, active "
            "FROM cam_instruments ORDER BY ticker ASC"
        )
    )
    return [
        {
            "ticker": m["ticker"],
            "asset_class": m["asset_class"],
            "exchange": m["exchange"],
            "contract_size": str(m["contract_size"]),
            "tick_size": str(m["tick_size"]),
            "point_value": str(m["point_value"]),
            "active": m["active"],
        }
        for m in (dict(r._mapping) for r in result.fetchall())
    ]
