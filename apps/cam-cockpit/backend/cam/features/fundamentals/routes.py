"""
Router FastAPI da feature `fundamentals` — TASK-U006 (BL-UI-0).

Expõe fundamentals (7 indicadores R-20), calendário de dividendos e os
alertas do Policy Engine (Carteira Hard) para a UI.

Princípio constitucional (Art. 23º + R-13): Policy Engine **sugere, nunca
bloqueia** — os alertas são informativos. Read-only.

Fase 0: fundamentals via `PlaceholderSource` (fixtures); scraping real é débito
(TD-v0.4-01). Calendário de dividendos ainda não tem fonte (TD-v0.5-DIVCAL).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session
from cam.features.fundamentals.multi_source_collector import PlaceholderSource
from cam.features.ledger.holdings import HoldingsRepository
from cam.features.ledger.policy_engine import evaluate_holding

router = APIRouter(prefix="/api/v1", tags=["fundamentals"])

_source = PlaceholderSource()
_holdings = HoldingsRepository()


@router.get("/fundamentals/{ticker}")
async def get_fundamentals(ticker: str) -> dict[str, Any]:
    """Snapshot fundamentalista (7 indicadores R-20). Read-only."""
    snap = await _source.fetch(ticker)
    if snap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NO_FUNDAMENTALS", "ticker": ticker.upper()},
        )
    return snap.to_dict()


@router.get("/dividends/calendar")
async def dividends_calendar() -> dict[str, Any]:
    """
    Calendário de dividendos (read-model Fase 0).

    Sem fonte de proventos conectada — estrutura estável + nota (TD-v0.5-DIVCAL).
    """
    return {
        "events": [],
        "note": "Fase 0: fonte de proventos não conectada (TD-v0.5-DIVCAL).",
    }


@router.get("/carteira-hard/policy-alerts")
async def policy_alerts(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Alertas do Policy Engine por holding. **Sugestão, nunca bloqueio** (R-13).

    `blocking` é sempre `false` na borda HTTP — a UI exibe banner amarelo.
    """
    holdings = await _holdings.list_all(session)
    alerts_out: list[dict[str, Any]] = []
    for h in holdings:
        snap = await _source.fetch(h["ticker"])
        fundamentals = snap.to_dict() if snap else None
        alerts = evaluate_holding(h, fundamentals)
        for a in alerts:
            alerts_out.append({"ticker": h["ticker"], **a.to_dict()})
    return {
        "alerts": alerts_out,
        # Política do CaM: alertas nunca bloqueiam operação (R-13). A UI trata
        # como sugestão (banner amarelo). Sempre false na borda HTTP.
        "blocking": False,
    }
