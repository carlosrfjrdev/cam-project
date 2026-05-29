"""
Multi-Source Collector — TASK-034 (BL-F SPEC v0.4).

Esqueleto preparado para múltiplas fontes (StatusInvest, Fundamentus, ...).
**Coleta real fica em TD-v0.4-01.** Esta TASK entrega:
  - Protocol `FundamentalsSource`.
  - 1 fonte `PlaceholderSource` (fixture estática) para validar pipeline.
  - Persistência em `cam_fundamentals_snapshot` com dedup por hash.

Sem rede em CI.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class FundamentalsSnapshot:
    ticker: str
    source: str
    ts_snapshot: datetime
    dy: Decimal | None = None
    pl: Decimal | None = None
    pvp: Decimal | None = None
    roe: Decimal | None = None
    div_liq_ebitda: Decimal | None = None
    payout: Decimal | None = None
    roic: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "source": self.source,
            "ts_snapshot": self.ts_snapshot.isoformat(),
            "dy": str(self.dy) if self.dy is not None else None,
            "pl": str(self.pl) if self.pl is not None else None,
            "pvp": str(self.pvp) if self.pvp is not None else None,
            "roe": str(self.roe) if self.roe is not None else None,
            "div_liq_ebitda": (
                str(self.div_liq_ebitda) if self.div_liq_ebitda is not None else None
            ),
            "payout": str(self.payout) if self.payout is not None else None,
            "roic": str(self.roic) if self.roic is not None else None,
        }

    def compute_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class FundamentalsSource(Protocol):
    """Contrato genérico de fonte de fundamentalistas."""

    name: str

    async def fetch(self, ticker: str) -> FundamentalsSnapshot | None: ...


class PlaceholderSource:
    """Fonte placeholder — retorna fixture estática. Não acessa rede."""

    name = "placeholder"

    _FIXTURES: dict[str, dict[str, Decimal]] = {
        "PETR4": {
            "dy": Decimal("0.0850"),
            "pl": Decimal("4.20"),
            "pvp": Decimal("1.15"),
            "roe": Decimal("0.32"),
            "div_liq_ebitda": Decimal("0.95"),
            "payout": Decimal("0.45"),
            "roic": Decimal("0.28"),
        },
        "ITUB4": {
            "dy": Decimal("0.0610"),
            "pl": Decimal("8.50"),
            "pvp": Decimal("1.85"),
            "roe": Decimal("0.21"),
            "div_liq_ebitda": Decimal("0.10"),
            "payout": Decimal("0.55"),
            "roic": Decimal("0.18"),
        },
    }

    async def fetch(self, ticker: str) -> FundamentalsSnapshot | None:
        ticker_upper = ticker.upper()
        if ticker_upper not in self._FIXTURES:
            return None
        return FundamentalsSnapshot(
            ticker=ticker_upper,
            source=self.name,
            ts_snapshot=datetime.now(UTC),
            **self._FIXTURES[ticker_upper],
        )


class FundamentalsCollector:
    """Orquestra fontes + persistência. Multi-source-ready (futura)."""

    def __init__(self, sources: list[FundamentalsSource] | None = None) -> None:
        self.sources = sources or [PlaceholderSource()]

    async def collect(
        self,
        session: AsyncSession,
        ticker: str,
    ) -> FundamentalsSnapshot | None:
        """
        Tenta cada source em ordem. Persiste o primeiro snapshot retornado.
        Idempotente via hash.
        """
        for src in self.sources:
            snap = await src.fetch(ticker)
            if snap is None:
                continue
            await self._persist(session, snap)
            return snap
        return None

    async def _persist(
        self, session: AsyncSession, snap: FundamentalsSnapshot
    ) -> None:
        try:
            await session.execute(
                text(
                    "INSERT INTO cam_fundamentals_snapshot "
                    "(ticker, ts_snapshot, source, dy, pl, pvp, roe, "
                    " div_liq_ebitda, payout, roic, hash) "
                    "VALUES (:t, :ts, :src, :dy, :pl, :pvp, :roe, "
                    "        :dle, :pay, :roic, :hash)"
                ),
                {
                    "t": snap.ticker,
                    "ts": snap.ts_snapshot,
                    "src": snap.source,
                    "dy": snap.dy,
                    "pl": snap.pl,
                    "pvp": snap.pvp,
                    "roe": snap.roe,
                    "dle": snap.div_liq_ebitda,
                    "pay": snap.payout,
                    "roic": snap.roic,
                    "hash": snap.compute_hash(),
                },
            )
            await session.commit()
        except IntegrityError:
            await session.rollback()  # dedup
