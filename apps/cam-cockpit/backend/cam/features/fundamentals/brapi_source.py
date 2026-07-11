"""
BrapiSource — fonte de fundamentos/dividendos via brapi.dev.

ADR-014 / SPEC-Inspetor R-11, R-12, R-15. Implementa o Protocol
`FundamentalsSource` já existente. Mapeia os 7 indicadores R-20 quando a brapi
os fornece; campos ausentes ficam None (→ "N/A" na UI). Token via settings
(`.env`, nunca commitado).

**Modelo da brapi (importante):** os indicadores fundamentalistas NÃO vêm na
raiz do /quote — vivem nos MÓDULOS `defaultKeyStatistics` e `financialData`,
pedidos via `modules=` e que exigem plano PRO. Só `priceEarnings`,
`regularMarketPrice` e `dividendYield` aparecem na raiz. Por isso buscamos cada
indicador em múltiplos locais/nomes (raiz → defaultKeyStatistics → financialData).

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

_TIMEOUT = httpx.Timeout(10.0, connect=4.0)

# Módulos PRO que carregam os fundamentalistas (R-20). Pedidos via modules=.
_MODULES = "defaultKeyStatistics,financialData,summaryProfile"


def _dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return d


def _pick(result: dict[str, Any], *keys: str) -> Any:
    """
    Procura a 1ª chave presente (não-nula) varrendo: raiz do result,
    defaultKeyStatistics e financialData. brapi varia o local por plano/ativo.
    """
    dks = result.get("defaultKeyStatistics") or {}
    fin = result.get("financialData") or {}
    for k in keys:
        for scope in (result, dks, fin):
            v = scope.get(k)
            if v is not None:
                return v
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

    def _params(self) -> dict[str, Any]:
        p: dict[str, Any] = {
            "fundamental": "true",
            "dividends": "true",
            "modules": _MODULES,
        }
        if self.token:
            p["token"] = self.token
        return p

    @staticmethod
    def _snapshot_from(t: str, r: dict[str, Any], name: str) -> FundamentalsSnapshot:
        # Dívida Líq/EBITDA: brapi raramente expõe direto; deriva de
        # (totalDebt - cash) / ebitda quando possível; senão usa netDebtToEbitda.
        div_ebitda = _pick(r, "netDebtToEbitda")
        if div_ebitda is None:
            total_debt = _dec(_pick(r, "totalDebt"))
            cash = _dec(_pick(r, "totalCash", "cash"))
            ebitda = _dec(_pick(r, "ebitda"))
            if total_debt is not None and ebitda and ebitda != 0:
                net = total_debt - (cash or Decimal(0))
                div_ebitda = net / ebitda

        return FundamentalsSnapshot(
            ticker=t,
            source=name,
            ts_snapshot=datetime.now(UTC),
            dy=_dec(_pick(r, "dividendYield", "trailingAnnualDividendYield")),
            pl=_dec(_pick(r, "priceEarnings", "trailingPE", "forwardPE")),
            pvp=_dec(_pick(r, "priceToBook", "pvp")),
            roe=_dec(_pick(r, "returnOnEquity", "roe")),
            div_liq_ebitda=_dec(div_ebitda),
            payout=_dec(_pick(r, "payoutRatio", "payout")),
            # ROIC não é exposto pela brapi. NÃO usar returnOnAssets como
            # substituto (seria enganoso) — fica None → "N/A" honesto na UI.
            roic=_dec(_pick(r, "returnOnInvestedCapital", "roic")),
        )

    async def fetch(self, ticker: str) -> FundamentalsSnapshot | None:
        r = await self.fetch_raw(ticker)
        if r is None:
            return None
        return self._snapshot_from(ticker.strip().upper(), r, self.name)

    async def fetch_raw(self, ticker: str) -> dict[str, Any] | None:
        """Resposta crua do 1º result (fundamentos + dividendos + preço)."""
        t = ticker.strip().upper()
        data = await self._get_json(f"{self.base_url}/quote/{t}", self._params())
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
