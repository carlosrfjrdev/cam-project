"""
Router do Trade Analyzer.

POST /api/v1/trade-analyzer/analyze
  multipart: report (file, obrigatório) + ticks (file, opcional) + provider (form)
  → métricas determinísticas + narrativa da IA escolhida.
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from cam.features.trade_analyzer.schemas import AnalyzeResponse
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


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_route(
    report: UploadFile = File(...),
    provider: str = Form("anthropic"),
    ticks: UploadFile | None = File(None),
):
    report_bytes = await report.read()
    ticks_bytes = await ticks.read() if ticks is not None else None
    try:
        result = await analyze(report_bytes, ticks_bytes, provider)
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
