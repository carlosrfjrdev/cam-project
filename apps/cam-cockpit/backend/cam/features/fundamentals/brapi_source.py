"""
BrapiSource — fonte de fundamentos/dividendos via brapi.dev (free tier).

ADR-014 / SPEC-Inspetor R-11, R-12, R-15. Implementa o Protocol
`FundamentalsSource` já existente. Mapeia os 7 indicadores R-20 quando a brapi
os fornece; campos ausentes ficam None (→ "N/A" na UI). Sem scraping
(scraping fica em TD-v0.4-01). Token opcional via settings (`.env`, nunca
commitado).

Falha segura: qualquer erro de rede/parse → retorna None (o coletor cai para a
fonte de fallback). Sem rede em CI: o teste injeta um cliente fake.
"""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from cam._shared.config import settings
from cam.features.fundamentals.multi_source_collector import FundamentalsSnapshot

_TIMEOUT = httpx.Timeout(6.0, connect=3.0)


def _dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


class BrapiSource:
    """Fonte brapi.dev. `name="brapi"`."""

    name = "brapi"

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.brapi_base_url).rstrip("/")
        self.token = token if token is not None else settings.brapi_token
        self._client = client  # injetável para teste (sem rede em CI)

    async def _get_json(
        self, url: str, params: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            if self._client is not None:
                resp = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return None
            return resp.json()
        except (httpx.HTTPError, ValueError):
            return None

    async def fetch(self, ticker: str) -> FundamentalsSnapshot | None:
        t = ticker.strip().upper()
        params: dict[str, Any] = {"fundamental": "true", "dividends": "true"}
        if self.token:
            params["token"] = self.token

        data = await self._get_json(f"{self.base_url}/quote/{t}", params)
        if not data:
            return None
        results = data.get("results") or []
        if not results:
            return None
        r = results[0]

        snap = FundamentalsSnapshot(
            ticker=t,
            source=self.name,
            ts_snapshot=datetime.now(UTC),
            dy=_dec(r.get("dividendYield") or r.get("dividend_yield")),
            pl=_dec(r.get("priceEarnings")),
            pvp=_dec(r.get("priceToBook") or r.get("price_to_book") or r.get("pvp")),
            roe=_dec(r.get("returnOnEquity") or r.get("roe")),
            div_liq_ebitda=_dec(
                r.get("netDebtToEbitda") or r.get("net_debt_to_ebitda")
            ),
            payout=_dec(r.get("payoutRatio") or r.get("payout")),
            roic=_dec(r.get("returnOnInvestedCapital") or r.get("roic")),
        )
        return snap

    async def fetch_raw(self, ticker: str) -> dict[str, Any] | None:
        """Resposta crua (para extrair histórico de dividendos + preço atual)."""
        t = ticker.strip().upper()
        params: dict[str, Any] = {"fundamental": "true", "dividends": "true"}
        if self.token:
            params["token"] = self.token
        data = await self._get_json(f"{self.base_url}/quote/{t}", params)
        if not data:
            return None
        results = data.get("results") or []
        return results[0] if results else None


def extract_dividends(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Normaliza o histórico de proventos da resposta brapi → lista canônica."""
    div = raw.get("dividendsData") or {}
    cash = div.get("cashDividends") or []
    out: list[dict[str, Any]] = []
    for d in cash:
        out.append(
            {
                "date": d.get("paymentDate") or d.get("lastDatePrior") or d.get("date"),
                "type": (d.get("label") or "DIVIDEND").upper(),
                "value": d.get("rate"),
            }
        )
    return out
