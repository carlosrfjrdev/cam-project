"""
Router do Trade Analyzer.

POST /api/v1/trade-analyzer/analyze
  multipart: report (file, obrigatório) + ticks (file, opcional) + provider (form)
  → métricas determinísticas + narrativa da IA escolhida.
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text

from cam._shared.infra import async_session_factory
from cam.features.trade_analyzer import repository
from cam.features.trade_analyzer.schemas import (
    AnalyzeResponse,
    HistoryItem,
    LastTickResponse,
)
from cam.features.trade_analyzer.service import (
    EmptyReportError,
    ProviderNotConfiguredError,
    analyze,
)

router = APIRouter(prefix="/api/v1/trade-analyzer", tags=["trade-analyzer"])


@router.get("/providers")
async def list_providers() -> dict:
    """Providers disponíveis para o seletor da UI."""
    from cam._shared.config import settings

    return {
        "providers": [
            {
                "id": "anthropic",
                "label": "Claude (Anthropic)",
                "model": settings.anthropic_model,
                "configured": bool(settings.anthropic_api_key),
            },
            {
                "id": "openai",
                "label": "OpenAI (GPT)",
                "model": settings.openai_model,
                "configured": bool(settings.openai_api_key),
            },
        ]
    }


@router.get("/last-tick", response_model=LastTickResponse)
async def last_tick() -> LastTickResponse:
    """
    Data/hora do último tick vindo do MT5 (corpus cam_market_ticks) + se a
    bridge está online. Alimenta o chip de frescor na tela.
    """
    bridge_online = False
    try:
        from cam.features.mt5_integration.routes import _service as mt5

        bridge_online = mt5.bridge.is_alive()
    except Exception:  # noqa: BLE001
        pass

    asset = ts = source = None
    try:
        async with async_session_factory() as session:
            row = (
                await session.execute(
                    text(
                        "SELECT asset, timestamp, source FROM cam_market_ticks "
                        "WHERE source LIKE 'mt5%' ORDER BY timestamp DESC LIMIT 1"
                    )
                )
            ).first()
        if row:
            asset = row[0]
            ts = row[1].isoformat() if row[1] else None
            source = row[2]
    except Exception:  # noqa: BLE001 — sem tabela/ticks ainda → null
        pass

    return LastTickResponse(
        asset=asset, timestamp=ts, source=source, bridge_online=bridge_online
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_route(
    report: UploadFile = File(...),
    provider: str = Form("anthropic"),
):
    report_bytes = await report.read()
    filename = report.filename or "report.csv"
    try:
        result = await analyze(report_bytes, provider, report_filename=filename)
    except EmptyReportError as exc:
        return JSONResponse(status_code=422, content={"error": str(exc)})
    except ProviderNotConfiguredError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:  # noqa: BLE001 — falha de rede/provider vira 502
        return JSONResponse(
            status_code=502,
            content={"error": f"Falha ao chamar IA ({provider}): {exc}"},
        )
    return AnalyzeResponse(**result)


@router.get("/history", response_model=list[HistoryItem])
async def history(limit: int = 100, offset: int = 0):
    return await repository.list_analyses(limit=limit, offset=offset)


@router.get("/history/{analysis_id}")
async def history_detail(analysis_id: int):
    rec = await repository.get_analysis(analysis_id)
    if rec is None:
        return JSONResponse(status_code=404, content={"error": "não encontrada"})
    return rec


@router.get("/history/{analysis_id}/report")
async def history_report(analysis_id: int):
    rec = await repository.get_report(analysis_id)
    if rec is None:
        return JSONResponse(status_code=404, content={"error": "report não encontrado"})
    filename, content = rec
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
