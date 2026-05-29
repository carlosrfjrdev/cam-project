"""
Carteira Hard Holdings — TASK-020/021/022/023 (BL-D SPEC v0.4).

Holdings de **patrimônio** (Art. 23). Nunca entram em margem do Risk Engine.

Operações:
  - HoldingsRepository.create, list, get_by_ticker.
  - GenialHoldingsService.import_from_parsed: ingere ParsedExtrato (T014).
  - assert_not_in_risk: rejeita add_open_position com asset não-derivativo (T023).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cam.features.ledger.genial_importer import ParsedExtrato


# ---------------------------------------------------------------------------
# Schema interno
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HoldingIn:
    ticker: str
    quantity: Decimal
    avg_price: Decimal
    asset_class: str = "equity"
    acquired_at: datetime | None = None
    source: str = "MANUAL_UI"


class HoldingValidationError(ValueError):
    """Validação de entrada falhou (quantidade não-positiva, source inválido, …)."""


class InvalidAssetForRiskError(RuntimeError):
    """
    Holdings nunca entram em margem do Risk Engine (Art. 23).
    Levantado quando alguém tenta adicionar PETR4 (não-derivativo) ao
    `OrderCandidate.add_open_position`.
    """


# ---------------------------------------------------------------------------
# Helper hash
# ---------------------------------------------------------------------------
def _compute_holding_hash(
    ticker: str,
    quantity: Decimal,
    avg_price: Decimal,
    acquired_at: datetime,
    source: str,
) -> str:
    raw = f"{ticker}|{quantity}|{avg_price}|{acquired_at.isoformat()}|{source}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate(holding: HoldingIn) -> None:
    if not holding.ticker or len(holding.ticker) > 20:
        raise HoldingValidationError(f"Ticker inválido: {holding.ticker!r}")
    if holding.quantity <= 0:
        raise HoldingValidationError(
            f"Quantidade deve ser positiva (atual: {holding.quantity})"
        )
    if holding.avg_price <= 0:
        raise HoldingValidationError(
            f"avg_price deve ser positivo (atual: {holding.avg_price})"
        )
    if holding.source not in ("MANUAL_UI", "GENIAL_IMPORT"):
        raise HoldingValidationError(
            f"source inválido: {holding.source!r} (esperado MANUAL_UI ou GENIAL_IMPORT)"
        )
    if holding.asset_class not in ("equity", "fii", "etf", "other"):
        raise HoldingValidationError(
            f"asset_class derivativo proibido em carteira hard: {holding.asset_class}"
        )


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------
class HoldingsRepository:
    async def create(
        self,
        session: AsyncSession,
        holding: HoldingIn,
    ) -> UUID | None:
        """
        Persiste novo holding. Retorna id se inserido, None se duplicado (hash).
        """
        _validate(holding)
        acquired = holding.acquired_at or datetime.now(UTC)
        h = _compute_holding_hash(
            holding.ticker, holding.quantity, holding.avg_price, acquired,
            holding.source,
        )
        try:
            result = await session.execute(
                text(
                    "INSERT INTO cam_carteira_hard_holdings "
                    "(ticker, asset_class, quantity, avg_price, "
                    " first_acquisition_at, last_acquisition_at, source, hash) "
                    "VALUES (:ticker, :ac, :qty, :px, :acq, :acq, :src, :hash) "
                    "RETURNING id"
                ),
                {
                    "ticker": holding.ticker.upper(),
                    "ac": holding.asset_class,
                    "qty": holding.quantity,
                    "px": holding.avg_price,
                    "acq": acquired,
                    "src": holding.source,
                    "hash": h,
                },
            )
            row = result.fetchone()
            await session.commit()
            return UUID(str(row[0])) if row else None
        except IntegrityError:
            await session.rollback()
            return None

    async def list_all(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            text(
                "SELECT id, ticker, asset_class, quantity, avg_price, "
                "       first_acquisition_at, last_acquisition_at, source "
                "FROM cam_carteira_hard_holdings ORDER BY ticker ASC"
            )
        )
        return [dict(row._mapping) for row in result.fetchall()]


# ---------------------------------------------------------------------------
# Importer Genial → Holdings (TASK-022)
# ---------------------------------------------------------------------------
class GenialHoldingsService:
    def __init__(self, repository: HoldingsRepository | None = None) -> None:
        self.repository = repository or HoldingsRepository()

    async def import_from_parsed(
        self,
        session: AsyncSession,
        parsed: ParsedExtrato,
    ) -> dict[str, int]:
        """
        Ingere ParsedExtrato.holdings → cam_carteira_hard_holdings.

        Retorna {"created": N, "duplicated": M, "skipped": K}.
        """
        created = 0
        duplicated = 0
        skipped = 0
        if parsed.requires_layout_confirmation:
            skipped = len(parsed.holdings)
            return {"created": 0, "duplicated": 0, "skipped": skipped}

        for row in parsed.holdings:
            try:
                holding = HoldingIn(
                    ticker=row.ticker,
                    quantity=Decimal(row.quantity),
                    avg_price=row.avg_price,
                    acquired_at=row.acquired_at,
                    source="GENIAL_IMPORT",
                )
                sid = await self.repository.create(session, holding)
                if sid is None:
                    duplicated += 1
                else:
                    created += 1
            except HoldingValidationError:
                skipped += 1
        return {"created": created, "duplicated": duplicated, "skipped": skipped}


# ---------------------------------------------------------------------------
# T023 — Defesa estrutural: holdings nunca entram em margem
# ---------------------------------------------------------------------------
def assert_can_add_to_risk(asset: str) -> None:
    """
    Levanta InvalidAssetForRiskError se asset não for derivativo.
    Risk Engine `add_open_position` consome esta defesa.
    Art. 23º — Carteira Hard = patrimônio, nunca margem.
    """
    derivatives = {"WIN", "WDO", "IND", "DOL"}
    if asset.upper() not in derivatives:
        raise InvalidAssetForRiskError(
            f"Asset '{asset}' é não-derivativo (Art. 23º). "
            f"Holdings de patrimônio não entram em margem. "
            f"Derivativos permitidos: {sorted(derivatives)}."
        )
