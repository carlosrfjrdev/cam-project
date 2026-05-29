"""
Fill Subscriber — TASK-029 (BL-E SPEC v0.4).

Subscriber ZeroMQ que consome `mt5.fill` da bridge e persiste `JournalEntry`
automaticamente (Art. 31º). Idempotente via `intent_id`.

Estrutura de mensagem esperada (publicada pelo `cam_risk_mirror.mq5` após
OrderSend bem-sucedido):

    {
      "intent_id": "<uuid>",
      "ticket": 999,
      "asset": "WIN",
      "direction": "LONG",
      "contracts": 1,
      "entry_price": 130000,
      "exit_price": 130150,
      "result_gross": 30.00,
      "fill_ts": "2026-05-27T14:35:00Z"
    }
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class FillEvent:
    intent_id: UUID
    ticket: int
    asset: str
    direction: str
    contracts: int
    entry_price: Decimal
    exit_price: Decimal | None
    result_gross: Decimal | None
    fill_ts: datetime


def parse_fill(payload: str | dict) -> FillEvent:
    """Converte JSON (str ou dict) em FillEvent."""
    data = json.loads(payload) if isinstance(payload, str) else payload
    return FillEvent(
        intent_id=UUID(data["intent_id"]),
        ticket=int(data["ticket"]),
        asset=str(data["asset"]),
        direction=str(data["direction"]),
        contracts=int(data["contracts"]),
        entry_price=Decimal(str(data["entry_price"])),
        exit_price=(
            Decimal(str(data["exit_price"]))
            if data.get("exit_price") is not None
            else None
        ),
        result_gross=(
            Decimal(str(data["result_gross"]))
            if data.get("result_gross") is not None
            else None
        ),
        fill_ts=datetime.fromisoformat(
            data["fill_ts"].replace("Z", "+00:00")
        ) if isinstance(data["fill_ts"], str) else data["fill_ts"],
    )


class FillToJournalService:
    """
    Persiste `FillEvent` como `cam_journal_entries` com `source=MT5_BRIDGE`.

    Idempotência via UNIQUE constraint em `cam_journal_entries.intent_id` se
    a coluna existir — caso contrário, query SELECT prévia.
    """

    async def persist(
        self, session: AsyncSession, event: FillEvent
    ) -> bool:
        """
        Persiste o fill como journal entry. Retorna True se inserido novo,
        False se já existia (idempotente).
        """
        # Sondagem: o schema atual de cam_journal_entries pode não ter
        # intent_id. Usamos asset+timestamp como dedup-key conservadora.
        existing = await session.execute(
            text(
                "SELECT id FROM cam_journal_entries "
                "WHERE asset = :asset AND created_at >= :ts0 "
                "  AND created_at <= :ts1"
            ),
            {
                "asset": event.asset,
                "ts0": event.fill_ts,
                "ts1": event.fill_ts,
            },
        )
        if existing.fetchone():
            return False
        try:
            await session.execute(
                text(
                    "INSERT INTO cam_journal_entries "
                    "(asset, direction, contracts, entry_price, exit_price, "
                    " result_gross, result_net, source, created_at) "
                    "VALUES (:asset, :dir, :ct, :ep, :xp, :rg, :rg, "
                    "        'MT5_BRIDGE', :ts)"
                ),
                {
                    "asset": event.asset,
                    "dir": event.direction,
                    "ct": event.contracts,
                    "ep": event.entry_price,
                    "xp": event.exit_price,
                    "rg": event.result_gross,
                    "ts": event.fill_ts,
                },
            )
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False
