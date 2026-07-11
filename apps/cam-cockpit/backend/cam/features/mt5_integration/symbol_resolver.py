"""
Resolução de símbolo — ticker B3 ↔ símbolo MT5 + classificação de tipo.

Inspetor de Ativo (ADR-014 / SPEC-Inspetor R-08, R-13). Read-only, puro.

Regras (heurísticas B3):
- Futuros: prefixo WIN/WDO/IND/DOL ou contém '$' (contrato contínuo) → "future"
- FII: 4 letras + "11" → "fii"
- Ação: 4 letras + dígito 3/4/5/6 → "stock"
- Caso contrário → "unknown" (tratado como genérico)

A normalização para o símbolo MT5 é mínima no MVP: upper + strip. O EA é a
autoridade sobre o nome exato (GET_SYMBOLS); este módulo apenas classifica e
oferece candidatos.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

AssetKind = Literal["stock", "fii", "future", "unknown"]

_FUTURE_PREFIXES = ("WIN", "WDO", "IND", "DOL")
_FII_RE = re.compile(r"^[A-Z]{4}11$")
_STOCK_RE = re.compile(r"^[A-Z]{4}(3|4|5|6)$")


@dataclass(frozen=True)
class ResolvedSymbol:
    ticker: str          # entrada normalizada (upper)
    mt5_symbol: str      # candidato de símbolo MT5
    kind: AssetKind
    has_fundamentals: bool  # True só para stock/fii

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "mt5_symbol": self.mt5_symbol,
            "type": self.kind,
            "has_fundamentals": self.has_fundamentals,
        }


def classify(ticker: str) -> AssetKind:
    t = (ticker or "").strip().upper()
    if not t:
        return "unknown"
    if "$" in t or t.startswith(_FUTURE_PREFIXES):
        return "future"
    if _FII_RE.match(t):
        return "fii"
    if _STOCK_RE.match(t):
        return "stock"
    return "unknown"


def resolve(ticker: str) -> ResolvedSymbol:
    t = (ticker or "").strip().upper()
    kind = classify(t)
    return ResolvedSymbol(
        ticker=t,
        mt5_symbol=t,  # MVP: símbolo B3 == símbolo MT5 (sem sufixo .SA)
        kind=kind,
        has_fundamentals=kind in ("stock", "fii"),
    )
