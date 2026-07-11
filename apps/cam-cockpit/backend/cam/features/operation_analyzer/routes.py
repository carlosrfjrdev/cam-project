"""
Router do Operation Analyzer (CASCA).

POST /api/v1/operation-analyzer/signal
  form: strategy + symbol + point_value + date (opc, default hoje) + timeframe
  → ticks + candles vêm AUTOMATICAMENTE do MT5 (bridge). Retorna SignalResponse
  com dados STUB (engine de sinais entra depois).

SEM bloqueios de Risk Manager (risk_manager_blocking=false) por design.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse

from cam.features.operation_analyzer.chart_service import (
    ALL_TFS,
    LEVEL_TFS,
    ChartUnavailable,
    build_chart,
)
from cam.features.operation_analyzer.schemas import (
    RiskAnalysis,
    Signal,
    SignalResponse,
)

router = APIRouter(prefix="/api/v1/operation-analyzer", tags=["operation-analyzer"])
BR_TZ = ZoneInfo("America/Sao_Paulo")


@router.get("/timeframes")
async def timeframes() -> dict:
    """TFs disponíveis e em quais há detecção de topos/fundos."""
    return {"timeframes": ALL_TFS, "level_timeframes": sorted(LEVEL_TFS)}


@router.get("/chart")
async def chart(
    symbol: str = Query(..., min_length=1),
    timeframe: str = Query("M5"),
    count: int = Query(1500, ge=50, le=5000),
    span: int = Query(3, ge=1, le=20),
    tol: float = Query(0.0015, ge=0.0, le=0.05),
    min_touches: int = Query(2, ge=1, le=10),
    top_n: int = Query(12, ge=1, le=50),
):
    """
    Candles + indicadores (EMA/SMA/VWAP) + topos/fundos (D1/H1/M10/M2). Persiste
    os candles importados. `span`/`tol`/`min_touches`/`top_n` calibram os níveis.
    """
    try:
        return await build_chart(
            symbol.upper(), timeframe.upper(), count,
            span=span, tol=tol, min_touches=min_touches, top_n=top_n,
        )
    except ChartUnavailable as exc:
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=502, content={"error": f"falha: {exc}"})


async def _fetch_market(symbol: str, day: datetime, timeframe: str) -> dict:
    """Ticks do dia + candles conforme provider. Falha segura → counts 0 + status."""
    from cam.features.app_settings import store

    provider = store.get_market_data_provider()
    if provider != "mt5":
        return {
            "ticks": 0,
            "candles": 0,
            "status": f"provedor '{provider}' em casca — ative MT5 nas Configurações",
        }
    try:
        from cam.features.mt5_integration.routes import _service as mt5
    except Exception:  # noqa: BLE001
        return {"ticks": 0, "candles": 0, "status": "integração MT5 indisponível"}
    if not mt5.bridge.is_alive():
        return {
            "ticks": 0,
            "candles": 0,
            "status": "bridge MT5 offline — atache o EA cam_bridge",
        }
    start = day.replace(hour=0, minute=0, second=0, tzinfo=BR_TZ) - timedelta(hours=3)
    end = day.replace(hour=23, minute=59, second=59, tzinfo=BR_TZ)
    from_msc = int(start.timestamp() * 1000)
    to_msc = int(end.timestamp() * 1000)
    n_ticks = n_candles = 0
    try:
        ticks = await mt5.get_ticks_range(symbol, from_msc, to_msc)
        n_ticks = len(ticks)
    except Exception:  # noqa: BLE001
        pass
    try:
        resp = await mt5.get_candles(symbol, timeframe, 500)
        n_candles = len(resp.get("data", {}).get("candles", []))
    except Exception:  # noqa: BLE001
        pass
    return {"ticks": n_ticks, "candles": n_candles, "status": "ok"}


@router.post("/signal", response_model=SignalResponse)
async def signal_route(
    strategy: str = Form("(não informada)"),
    symbol: str = Form("WINM26"),
    point_value: float = Form(0.20),
    date: str = Form(""),
    timeframe: str = Form("M5"),
):
    try:
        day = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now(BR_TZ)
    except ValueError:
        day = datetime.now(BR_TZ)

    market = await _fetch_market(symbol, day, timeframe)

    # --- STUB: engine de sinais ainda não implementada (casca) ---
    suggested_size = 1
    risk_points = 100.0
    risk_per_trade = round(risk_points * point_value * suggested_size, 2)

    stub_signals = [
        Signal(
            time="11:05",
            side="LONG",
            entry=170900.0,
            stop=170800.0,
            target=171200.0,  # R:R 1:3 sobre 100 pts de risco
            size=suggested_size,
            risk_points=risk_points,
            rationale="STUB — exemplo de sinal a R:R 1:3 na janela de edge (11h).",
        )
    ]

    return SignalResponse(
        status="STUB",
        symbol=symbol,
        strategy=strategy,
        inputs={
            "ticks_rows": market["ticks"],
            "candles_rows": market["candles"],
            "point_value": point_value,
            "tick_status": market["status"],
            "date": day.strftime("%Y-%m-%d"),
        },
        risk_analysis=RiskAnalysis(
            suggested_size=suggested_size,
            best_hour="11:00–12:00",
            risk_per_trade=risk_per_trade,
            max_risk_session=round(risk_per_trade * 3, 2),
            risk_manager_blocking=False,
        ),
        signals=stub_signals,
        notes=(
            "CASCA: ticks+candles vêm AUTO do MT5; sinais ainda são STUB. Próximo "
            "passo é plugar a engine (estratégia + ticks/candles → sinais reais). "
            "Sem bloqueio de Risk Manager: o risco é exibido como análise."
        ),
    )
