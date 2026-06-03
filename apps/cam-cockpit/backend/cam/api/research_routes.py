"""
Composição das rotas da Research Lane — vive em cam/api/ (compositor autorizado
por ADR-013 a conhecer múltiplas features). Liga o serviço de research (que NÃO
importa MT5) à fonte de dado (bridge MT5) por injeção de callables na borda.

Mantém o contrato import-linter "Research Lane nao importa execucao nem broker"
verde: o slice cam.features.research nunca importa mt5_integration; o
acoplamento é feito AQUI, no compositor.

SPEC v0.5 §4.1 — namespace /api/v1/research, read-only. POST /ingest cria job de
pesquisa (não ordem). Sub-versão 0.5.1: ingest + data-health.
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from cam._shared.infra import async_session_factory
from cam.features.mt5_integration.routes import _service as _mt5_service
from cam.features.research.leadlag.service import LeadLagIngestionService

router = APIRouter(prefix="/api/v1/research", tags=["research-leadlag"])

_ingestion = LeadLagIngestionService(async_session_factory)

# Universo SEED (parametrizável — UNIV): WIN/WDO + 6 maiores do IBOV.
SEED_UNIVERSE = ["WIN$", "WDO$", "VALE3", "ITUB4", "PETR4", "AXIA3", "BBDC4", "B3SA3"]


class IngestRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: list(SEED_UNIVERSE))
    timeframes: list[str] = Field(
        default_factory=lambda: ["M5", "M15", "M30", "H1", "H4", "D1"]
    )
    count: int = Field(default=5000, ge=1, le=50000)  # "máximo que o MT5 entregar"
    with_ticks: bool = True
    tick_count: int = Field(default=2000, ge=1, le=5000)


async def _candle_fetcher(symbol: str, timeframe: str, count: int) -> dict[str, Any]:
    """
    Borda: chama o bridge MT5. O serviço de research recebe isto injetado.

    Ingestão pede milhares de M1 → timeout grande (10s). O EA, na 1ª chamada de
    um símbolo, dispara o download assíncrono do histórico (CopyRates) e pode
    voltar vazio/curto: por isso seleciona o símbolo (SUBSCRIBE) e faz alguns
    retries até o histórico sincronizar.
    """
    try:
        await _mt5_service.subscribe_symbol(symbol)
    except Exception:
        pass
    last: dict[str, Any] = {"status": "error", "error": "NO_DATA"}
    for _ in range(4):
        resp = await _mt5_service.get_candles(
            symbol, timeframe, count, timeout_ms=10000
        )
        if resp.get("status") == "ok" and resp.get("data", {}).get("candles"):
            return resp
        last = resp
        await asyncio.sleep(1.0)  # dá tempo do CopyRates sincronizar
    return last


async def _tick_fetcher(symbol: str, count: int) -> dict[str, Any]:
    """Borda: PROBE_TICKS traz ticks com flags (agressor)."""
    return await _mt5_service.probe_ticks(symbol, count)


@router.post("/ingest")
async def ingest(body: IngestRequest):
    """
    Ingestão parametrizável MT5 → research_* (R-01). Cria job de pesquisa, NUNCA
    ordem (Kevin). Falha segura se o bridge estiver offline (R-05).
    """
    if not _mt5_service.bridge.is_alive():
        return JSONResponse(
            status_code=503,
            content={"error": "MT5_BRIDGE_OFFLINE", "message": "Abra o MT5 + EA."},
        )
    result = await _ingestion.ingest(
        sources=body.sources,
        timeframes=body.timeframes,
        count=body.count,
        with_ticks=body.with_ticks,
        candle_fetcher=_candle_fetcher,
        tick_fetcher=_tick_fetcher,
        tick_count=body.tick_count,
    )
    return result


@router.get("/data-health")
async def data_health():
    """Cobertura por símbolo/TF + liquidez de tick (R-08). Antes de qualquer análise."""
    health = await _ingestion.data_health()
    return {"seed_universe": SEED_UNIVERSE, **health}
