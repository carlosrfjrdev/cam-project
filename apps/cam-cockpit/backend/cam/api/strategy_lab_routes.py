"""
Composição das rotas do StrategyLab — vive em cam/api/ (compositor autorizado a
conhecer features — ADR-013). Liga o serviço (que NÃO importa MT5 nem execução)
às bordas HTTP. Namespace /api/v1/strategy-lab.

Tríade:
  - Assets Strategy  → catálogo + params + otimizador on-demand (sugere).
  - Assets RunTests  → backtest bruto + equity + trades + paridade.
  - Assets Experts   → recebe o ledger do EA e roda a paridade (gate).

MVP de valores BRUTOS (R-11). Nenhum endpoint envia ordem. O otimizador SUGERE,
nunca aplica (R-08).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from cam._shared.infra import async_session_factory
from cam.features.strategy_lab.service import StrategyLabService

router = APIRouter(prefix="/api/v1/strategy-lab", tags=["strategy-lab"])

_service = StrategyLabService(async_session_factory)


# --------------------------------------------------------------------------- #
# Assets Strategy — catálogo
# --------------------------------------------------------------------------- #
@router.get("/strategies")
async def list_strategies():
    """Lista as estratégias do catálogo (Onda 1: só D1 runnable)."""
    return {"strategies": _service.list_strategies(), "label": "BRUTO"}


@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    sd = _service.get_strategy(strategy_id)
    if sd is None:
        return JSONResponse(status_code=404, content={"error": "STRATEGY_NOT_FOUND"})
    return sd


# --------------------------------------------------------------------------- #
# Assets RunTests — backtest
# --------------------------------------------------------------------------- #
class BacktestRequest(BaseModel):
    symbol: str
    timeframe: str = "M1"
    params: dict[str, Any] = Field(default_factory=dict)
    point_value: float = Field(default=0.20, gt=0.0)
    qty: int = Field(default=1, ge=1)
    window_start: datetime | None = None
    window_end: datetime | None = None
    param_set_id: int | None = None


@router.post("/strategies/{strategy_id}/backtest")
async def run_backtest(strategy_id: str, body: BacktestRequest):
    """
    Roda o backtest bruto da estratégia (single-symbol). Falha explícita se o
    símbolo não tiver dado em research_bars (T-007).
    """
    result = await _service.run_backtest(
        strategy_id=strategy_id,
        symbol=body.symbol,
        timeframe=body.timeframe,
        params=body.params,
        point_value=body.point_value,
        qty=body.qty,
        window_start=body.window_start,
        window_end=body.window_end,
        param_set_id=body.param_set_id,
    )
    if result.get("error") == "NO_DATA":
        return JSONResponse(status_code=422, content=result)
    if result.get("error") == "STRATEGY_NOT_RUNNABLE":
        return JSONResponse(status_code=400, content=result)
    return result


# --------------------------------------------------------------------------- #
# Assets Strategy — otimizador on-demand
# --------------------------------------------------------------------------- #
class OptimizeRequest(BaseModel):
    symbol: str
    timeframe: str = "M1"
    space: dict[str, list] | None = None      # None → param_space do catálogo
    method: str = Field(default="grid", pattern="^(grid|random)$")
    random_n: int = Field(default=50, ge=1, le=2000)
    seed: int = 42
    min_trades: int = Field(default=20, ge=2)
    point_value: float = Field(default=0.20, gt=0.0)
    qty: int = Field(default=1, ge=1)
    window_start: datetime | None = None
    window_end: datetime | None = None


@router.post("/strategies/{strategy_id}/optimize")
async def run_optimize(strategy_id: str, body: OptimizeRequest):
    """
    Otimização on-demand (R-05). SUGERE o melhor conjunto com selo de robustez
    (DSR + no-cliff) e persiste como param_set origin='suggested' — NÃO aplica.
    """
    result = await _service.run_optimization(
        strategy_id=strategy_id,
        symbol=body.symbol,
        timeframe=body.timeframe,
        space=body.space,
        method=body.method,
        random_n=body.random_n,
        seed=body.seed,
        min_trades=body.min_trades,
        point_value=body.point_value,
        qty=body.qty,
        window_start=body.window_start,
        window_end=body.window_end,
    )
    if result.get("error") in {"NO_DATA", "NO_PARAM_SPACE"}:
        return JSONResponse(status_code=422, content=result)
    if result.get("error") == "STRATEGY_NOT_RUNNABLE":
        return JSONResponse(status_code=400, content=result)
    return result


# --------------------------------------------------------------------------- #
# Assets RunTests — leitura de resultado
# --------------------------------------------------------------------------- #
@router.get("/runs")
async def list_runs(strategy_id: str | None = None):
    return {"runs": await _service.list_runs(strategy_id)}


@router.get("/runs/{run_id}")
async def get_run(run_id: int):
    res = await _service.get_run(run_id)
    if res is None:
        return JSONResponse(status_code=404, content={"error": "RUN_NOT_FOUND"})
    return res


@router.get("/runs/{run_id}/equity-curve")
async def equity_curve(run_id: int):
    res = await _service.get_equity(run_id)
    if res is None:
        return JSONResponse(status_code=404, content={"error": "RUN_NOT_FOUND"})
    return res


# --------------------------------------------------------------------------- #
# Assets Experts — paridade Python ↔ EA (gate bloqueante)
# --------------------------------------------------------------------------- #
class ParityRequest(BaseModel):
    # ledger exportado pelo EA (cam_d1_orb30.mq5) no schema canônico.
    ea_ledger: list[dict[str, Any]]
    tick_size: float = Field(..., gt=0.0)


@router.post("/runs/{run_id}/parity")
async def run_parity(run_id: int, body: ParityRequest):
    """
    Compara o ledger Python (do run) com o ledger do EA, trade-a-trade. PASS =
    100% sinais + ≤1 tick + volume/qtd/motivo idênticos (R-29). FAIL → abre BUG.
    """
    res = await _service.run_parity(run_id, body.ea_ledger, body.tick_size)
    if res is None:
        return JSONResponse(status_code=404, content={"error": "RUN_NOT_FOUND"})
    status = 200 if res["verdict"] == "PASS" else 409
    return JSONResponse(status_code=status, content=res)
