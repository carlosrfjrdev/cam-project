"""
Router do Operation Analyzer (CASCA).

POST /api/v1/operation-analyzer/signal
  multipart: ticks (file, opc) + candles (file, opc) + strategy (form) +
             symbol (form) + point_value (form)
  → contrato SignalResponse com dados STUB. A engine real entra depois.

SEM bloqueios de Risk Manager (risk_manager_blocking=false) por design.
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from cam.features.operation_analyzer.schemas import (
    RiskAnalysis,
    Signal,
    SignalResponse,
)

router = APIRouter(prefix="/api/v1/operation-analyzer", tags=["operation-analyzer"])


def _count_lines(content: bytes | None) -> int:
    if not content:
        return 0
    return max(0, content.decode("utf-8", errors="replace").count("\n") - 1)


@router.post("/signal", response_model=SignalResponse)
async def signal_route(
    strategy: str = Form("(não informada)"),
    symbol: str = Form("WINM26"),
    point_value: float = Form(0.20),
    ticks: UploadFile | None = File(None),
    candles: UploadFile | None = File(None),
):
    ticks_bytes = await ticks.read() if ticks is not None else None
    candles_bytes = await candles.read() if candles is not None else None

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
            "ticks_rows": _count_lines(ticks_bytes),
            "candles_rows": _count_lines(candles_bytes),
            "point_value": point_value,
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
            "CASCA: contrato estável com dados STUB. Próximo passo é plugar a engine "
            "de sinais (estratégia + ticks/candles → sinais reais). Sem bloqueio de "
            "Risk Manager: o risco é exibido como análise, não como trava."
        ),
    )
