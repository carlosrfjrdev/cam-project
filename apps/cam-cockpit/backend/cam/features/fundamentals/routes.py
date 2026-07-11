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
from cam.features.fundamentals.brapi_source import (
    BrapiSource,
    extract_dividends,
)
from cam.features.fundamentals.dividends import project_dividends
from cam.features.fundamentals.multi_source_collector import PlaceholderSource
from cam.features.ledger.holdings import HoldingsRepository
from cam.features.ledger.policy_engine import evaluate_holding

router = APIRouter(prefix="/api/v1", tags=["fundamentals"])

_source = PlaceholderSource()
_brapi = BrapiSource()
_holdings = HoldingsRepository()


def _classify(ticker: str) -> str:
    t = ticker.strip().upper()
    if "$" in t or t.startswith(("WIN", "WDO", "IND", "DOL")):
        return "future"
    if len(t) == 6 and t.endswith("11"):
        return "fii"
    if len(t) == 5 and t[-1] in "3456":
        return "stock"
    return "unknown"


@router.get("/fundamentals/{ticker}")
async def get_fundamentals(ticker: str) -> dict[str, Any]:
    """
    Snapshot fundamentalista (7 indicadores R-20) + dividendos + 2 projeções.

    Fonte primária: brapi.dev (R-11). Fallback: PlaceholderSource (fixtures) —
    garante resposta útil em CI/offline. Read-only. Futuros não têm fundamentos.
    """
    t = ticker.strip().upper()
    kind = _classify(t)

    # brapi primeiro; fallback para placeholder (CI/offline)
    snap = await _brapi.fetch(t)
    raw = await _brapi.fetch_raw(t) if snap is not None else None
    source = "brapi"
    if snap is None:
        snap = await _source.fetch(t)
        source = "placeholder"

    if snap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NO_FUNDAMENTALS", "ticker": t},
        )

    dividends_history: list[dict[str, Any]] = []
    price = None
    if raw is not None:
        dividends_history = extract_dividends(raw)
        price = raw.get("regularMarketPrice")

    base = snap.to_dict()
    base["type"] = kind
    base["source"] = source
    base["dividends_history"] = dividends_history
    base["dividend_projection"] = project_dividends(dividends_history, price)
    return base


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
