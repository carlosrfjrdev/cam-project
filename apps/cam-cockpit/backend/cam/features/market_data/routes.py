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

from fastapi import APIRouter, File, UploadFile

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
