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
from cam.features.research.leadlag.run_service import LeadLagRunService
from cam.features.research.leadlag.service import LeadLagIngestionService

router = APIRouter(prefix="/api/v1/research", tags=["research-leadlag"])

_ingestion = LeadLagIngestionService(async_session_factory)
_runner = LeadLagRunService(async_session_factory)

# Universo SEED (parametrizável — UNIV): WIN/WDO + 6 maiores do IBOV.
SEED_UNIVERSE = ["WIN$", "WDO$", "VALE3", "ITUB4", "PETR4", "AXIA3", "BBDC4", "B3SA3"]


class IngestRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: list(SEED_UNIVERSE))
    timeframes: list[str] = Field(
        default_factory=lambda: ["M5", "M15", "M30", "H1", "H4", "D1"]
    )
    # blocos de 5000 (cam_bridge). 0 = EXTRAIR TUDO (loop até esgotar o histórico).
    count: int = Field(default=5000, ge=0, le=10_000_000)
    with_ticks: bool = True
    # ticks reais em bulk (GET_TICKS paginado). 0 = TODOS os ticks (loop até esgotar).
    tick_count: int = Field(default=2000, ge=0, le=200_000_000)


# Casa com InpMaxCandles do cam_bridge (cap por requisição p/ proteger heartbeat).
_CANDLE_CHUNK = 5000
# Guarda contra loop infinito no pooling (5000 blocos = 25M candles).
_MAX_ITERS = 5000


async def _candle_fetcher(symbol: str, timeframe: str, count: int) -> dict[str, Any]:
    """
    Borda: chama o bridge MT5. O serviço de research recebe isto injetado.

    POOLING DE EXTRAÇÃO (cam_bridge 0.4.1+): o EA limita cada GET_CANDLES a
    InpMaxCandles (5000) p/ não travar o heartbeat. Pedimos blocos sucessivos com
    `start_pos` crescente e concatenamos, **em LOOP até esgotar o histórico**
    (bloco curto = fim). `count <= 0` ⇒ EXTRAIR TUDO (sem teto). Retry só importa
    no 1º bloco (CopyRates sincroniza o histórico). Cada bloco vem ascendente;
    blocos mais ANTIGOS (pos maior) vêm ANTES.
    """
    try:
        await _mt5_service.subscribe_symbol(symbol)
    except Exception:
        pass
    all_mode = count <= 0
    collected: list[Any] = []
    last: dict[str, Any] = {"status": "error", "error": "NO_DATA"}
    pos = 0
    iters = 0
    while True:
        iters += 1
        if iters > _MAX_ITERS:
            break  # guarda contra loop infinito
        want = _CANDLE_CHUNK if all_mode else min(_CANDLE_CHUNK, count - len(collected))
        if want <= 0:
            break
        chunk: list[Any] | None = None
        for _ in range(4):
            resp = await _mt5_service.get_candles(
                symbol, timeframe, want, timeout_ms=15000, start_pos=pos
            )
            last = resp
            if resp.get("status") == "ok" and resp.get("data", {}).get("candles"):
                chunk = resp["data"]["candles"]
                break
            await asyncio.sleep(1.0)  # dá tempo do CopyRates sincronizar
        if not chunk:
            break  # sem mais histórico (ou bridge offline)
        collected = chunk + collected
        pos += len(chunk)
        if len(chunk) < want:
            break  # fim do histórico disponível (bloco curto)
    if not collected:
        return last
    return {
        "status": "ok",
        "data": {"symbol": symbol, "timeframe": timeframe, "candles": collected},
    }


async def _tick_fetcher(symbol: str, from_msc: int, count: int) -> dict[str, Any]:
    """Borda: GET_TICKS traz ticks reais em bulk (paginado por from_msc)."""
    return await _mt5_service.get_ticks(symbol, from_msc=from_msc, count=count)


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


@router.delete("/dataset")
async def purge_dataset(symbol: str | None = None):
    """
    Limpa o dataset (research_bars + research_ticks). `?symbol=WINM26` limpa só
    aquele papel; sem symbol limpa TUDO. Mantém runs/análises.
    """
    res = await _ingestion.purge_dataset(symbol)
    return {"purged": res, "symbol": (symbol.upper() if symbol else "ALL")}


# --------------------------------------------------------------------------- #
# 0.5.2 — análise de lead-lag (correlação defasada bar-time)
# --------------------------------------------------------------------------- #
class RunRequest(BaseModel):
    sources: list[str] = Field(..., min_length=1)
    target: str
    # grade de defasagem (lookback em barras) — "últimos 50 timeframes" = 1..50
    delta_grid: list[int] = Field(default_factory=lambda: list(range(1, 51)))
    timeframe: str = "M1"
    min_samples: int = Field(default=30, ge=2)
    cost: float = 0.0
    fdr_q: float = Field(default=0.05, gt=0.0, lt=1.0)  # taxa de falsa descoberta
    snapshot_id: int | None = None


@router.post("/runs")
async def create_run(body: RunRequest):
    """
    Lança uma análise de lead-lag parametrizável (R-25/R-30). Cria **job de
    pesquisa**, NUNCA ordem (Kevin). Retorna run_id + contador de tentativas.
    """
    return await _runner.run(
        sources=body.sources,
        target=body.target,
        delta_grid=body.delta_grid,
        timeframe=body.timeframe,
        min_samples=body.min_samples,
        cost=body.cost,
        fdr_q=body.fdr_q,
        snapshot_id=body.snapshot_id,
    )


@router.get("/runs")
async def list_runs():
    """Lista runs + status + contador de tentativas."""
    return {"runs": await _runner.list_runs()}


@router.get("/runs/{run_id}")
async def get_run(run_id: int):
    """Resultado: matriz C(δ) por par, n por célula, veredito (R-31)."""
    res = await _runner.get_result(run_id)
    if res is None:
        return JSONResponse(status_code=404, content={"error": "RUN_NOT_FOUND"})
    return res


@router.get("/stats/trials")
async def stats_trials():
    """Contador global de tentativas (alimenta a deflação estatística — 0.5.3)."""
    return {"total_trials": await _runner.total_trials()}
