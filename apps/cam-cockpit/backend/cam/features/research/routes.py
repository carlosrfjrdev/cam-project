"""
Router FastAPI da feature `research` — TASK-U005 (BL-UI-0).

Expõe o AI Workbench / Research (correlação cross-asset, pair-trade backtest,
workbench de IA governado) para a UI. **Somente research — nunca operação.**

Governança de provider (Kevin): OpenAI bloqueado (`OpenAINotEnabledError`,
TD-v0.4-02). Anthropic/Ollama permitidos.

Fase 0: não há store de séries de preço acessível ao endpoint de correlação —
`/correlation` retorna read-model (correlation=None) até a ingestão persistir
séries (TD-v0.5-PRICESERIES). `pair-trade-backtest` opera sobre séries do corpo.
"""
from __future__ import annotations

import math
from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from cam.features.ai_analyst.provider_governance import (
    OpenAINotEnabledError,
    call_provider,
)
from cam.features.research.cross_asset_correlation import (
    PricePoint,
    compute_correlation,
)
from cam.features.research.pair_trade_backtest import run_pair_backtest

router = APIRouter(prefix="/api/v1/research", tags=["research"])


class PricePointBody(BaseModel):
    timestamp: datetime
    price: Decimal


class PairBacktestRequest(BaseModel):
    asset_a: str
    asset_b: str
    series_a: list[PricePointBody]
    series_b: list[PricePointBody]
    window: int = 30
    zscore_threshold: float = 2.0


class WorkbenchRequest(BaseModel):
    provider: str = "ollama"
    prompt: str
    model: str = "default"


def _clean(x: float) -> float | None:
    return None if (x is None or math.isnan(x) or math.isinf(x)) else x


@router.get("/correlation")
async def correlation(
    asset_a: str = Query(default="WIN"),
    asset_b: str = Query(default="WDO"),
    window_days: int = Query(default=30),
) -> dict[str, Any]:
    """
    Correlação cross-asset (read-model Fase 0).

    Sem séries persistidas, retorna `correlation=None` e nota — não inventa dado.
    """
    result = compute_correlation(asset_a, asset_b, [], [], window_days=window_days)
    return {
        "asset_a": result.asset_a,
        "asset_b": result.asset_b,
        "correlation": _clean(result.correlation),
        "sample_size": result.sample_size,
        "window_days": result.window_days,
        "note": (
            "Fase 0: séries de preço ainda não persistidas para correlação "
            "(TD-v0.5-PRICESERIES)."
        ),
    }


@router.post("/pair-trade-backtest")
async def pair_trade_backtest(body: PairBacktestRequest) -> dict[str, Any]:
    """Backtest de pair trade sobre as séries fornecidas. Research-only."""
    series_a = [PricePoint(timestamp=p.timestamp, price=p.price) for p in body.series_a]
    series_b = [PricePoint(timestamp=p.timestamp, price=p.price) for p in body.series_b]
    res = run_pair_backtest(
        body.asset_a,
        body.asset_b,
        series_a,
        series_b,
        window=body.window,
        zscore_threshold=body.zscore_threshold,
    )
    return {
        "asset_a": res.asset_a,
        "asset_b": res.asset_b,
        "trades": len(res.trades),
        "total_pnl": _clean(res.total_pnl),
        "sharpe": _clean(res.sharpe),
        "correlation": (
            _clean(res.correlation.correlation) if res.correlation else None
        ),
    }


@router.post("/workbench")
async def workbench(body: WorkbenchRequest) -> dict[str, Any]:
    """
    AI Workbench governado — output estruturado.

    OpenAI → 422 `OpenAINotEnabled` (Kevin, TD-v0.4-02). Sem operação real.
    """
    try:
        record = await call_provider(
            body.provider,
            body.prompt,
            model=body.model,
            response=None,
            anonymized=True,
            session=None,
        )
    except OpenAINotEnabledError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "OpenAINotEnabled", "message": str(err)},
        ) from err
    return {
        "call_id": str(record.id),
        "provider": record.provider.value,
        "model": record.model,
        "prompt_hash": record.prompt_hash,
        "anonymized": record.anonymized,
        "ts": record.ts.isoformat(),
    }
