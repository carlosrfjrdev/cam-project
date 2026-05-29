"""
Instrument Catalog Loader — TASK-062 (BL-I SPEC v0.4).

Carrega ≥ 200 instrumentos em `cam_instruments` via CSV. Endpoint para ativar
por demanda. Default `active=false` para não inflar telas.
"""
from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class InstrumentRow:
    ticker: str
    asset_class: str
    exchange: str = "B3"
    contract_size: Decimal = Decimal("1")
    tick_size: Decimal = Decimal("0.01")
    point_value: Decimal = Decimal("1")
    active: bool = False


_VALID_ASSET_CLASSES = {"futures", "equity", "fii", "etf", "other"}


def parse_instruments_csv(path: str | Path) -> list[InstrumentRow]:
    """
    Parseia CSV com header: ticker,asset_class[,point_value,active].
    """
    rows: list[InstrumentRow] = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            ticker = (raw.get("ticker") or "").strip().upper()
            asset_class = (raw.get("asset_class") or "equity").strip().lower()
            if not ticker:
                continue
            if asset_class not in _VALID_ASSET_CLASSES:
                continue
            rows.append(
                InstrumentRow(
                    ticker=ticker,
                    asset_class=asset_class,
                    point_value=Decimal(raw.get("point_value", "1")),
                    active=(raw.get("active", "false").lower() == "true"),
                )
            )
    return rows


async def upsert_instruments(
    session: AsyncSession, rows: Iterable[InstrumentRow]
) -> int:
    """Idempotente: INSERT ... ON CONFLICT DO NOTHING."""
    count = 0
    for row in rows:
        result = await session.execute(
            text(
                "INSERT INTO cam_instruments "
                "(ticker, asset_class, exchange, contract_size, "
                " tick_size, point_value, active) "
                "VALUES (:t, :ac, :ex, :cs, :ts, :pv, :a) "
                "ON CONFLICT (ticker) DO NOTHING"
            ),
            {
                "t": row.ticker,
                "ac": row.asset_class,
                "ex": row.exchange,
                "cs": row.contract_size,
                "ts": row.tick_size,
                "pv": row.point_value,
                "a": row.active,
            },
        )
        if result.rowcount and result.rowcount > 0:
            count += 1
    await session.commit()
    return count


async def activate(session: AsyncSession, ticker: str) -> bool:
    """Ativa um ticker. Retorna True se mudou estado."""
    result = await session.execute(
        text(
            "UPDATE cam_instruments SET active = true "
            "WHERE ticker = :t AND active = false"
        ),
        {"t": ticker.upper()},
    )
    await session.commit()
    return bool(result.rowcount)
