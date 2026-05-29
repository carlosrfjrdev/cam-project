"""
Repository da feature journal — SQLAlchemy 2.0 async.

REGRA CONSTITUCIONAL: cam_journal_entries é IMUTÁVEL.
- Apenas INSERT — sem UPDATE, sem DELETE.
- Correções usam JournalCorrection com referência ao entry original.

Duplo journal (SPEC R11.06 / CA11.3):
- Persiste em cam_journal_entries (banco)
- Appenda em ~/.cam/journal/YYYY-MM-DD.jsonl (arquivo local)
"""
# sem update — sem delete (imutabilidade constitucional)
import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.domain.primitives import Money
from cam.features.journal.domain import JournalEntry

# Diretório do journal duplo JSONL
_JOURNAL_DIR = Path.home() / ".cam" / "journal"


def _entry_to_dict(entry_id: str, entry: JournalEntry) -> dict:
    """Serializa JournalEntry para dict (JSON-serializable)."""
    return {
        "id": entry_id,
        "asset": entry.asset,
        "direction": entry.direction,
        "contracts": entry.contracts,
        "entry_price": str(entry.entry_price),
        "exit_price": str(entry.exit_price),
        "result_gross": str(entry.result_gross.amount),
        "costs": str(entry.costs.amount),
        "tax_provisioned": str(entry.tax_provisioned.amount),
        "result_net": str(entry.result_net.amount),
        "strategy": entry.strategy,
        "setup": entry.setup,
        "adherence": entry.adherence,
        "emotional_note": entry.emotional_note,
        "lesson": entry.lesson,
        "source": entry.source,
        "created_at": datetime.now(UTC).isoformat(),
    }


def _append_to_jsonl(entry_id: str, entry: JournalEntry) -> None:
    """
    Appenda entry em ~/.cam/journal/YYYY-MM-DD.jsonl.

    Journal duplo: banco + arquivo local append-only.
    SPEC R11.06 / CA11.3.
    """
    _JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    jsonl_path = _JOURNAL_DIR / f"{today}.jsonl"
    record = _entry_to_dict(entry_id, entry)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class JournalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, entry: JournalEntry) -> str:
        """
        Persiste um JournalEntry — INSERT apenas, nunca UPDATE.

        Retorna o UUID gerado.
        Também appenda em ~/.cam/journal/YYYY-MM-DD.jsonl (journal duplo).
        """
        entry_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        await self._session.execute(
            text(
                """
                INSERT INTO cam_journal_entries (
                    id, asset, direction, contracts,
                    entry_price, exit_price,
                    result_gross, costs, tax_provisioned, result_net,
                    strategy, setup, adherence,
                    emotional_note, lesson, source,
                    created_at
                ) VALUES (
                    :id, :asset, :direction, :contracts,
                    :entry_price, :exit_price,
                    :result_gross, :costs, :tax_provisioned, :result_net,
                    :strategy, :setup, :adherence,
                    :emotional_note, :lesson, :source,
                    :created_at
                )
                """
            ),
            {
                "id": entry_id,
                "asset": entry.asset,
                "direction": entry.direction,
                "contracts": entry.contracts,
                "entry_price": str(entry.entry_price),
                "exit_price": str(entry.exit_price),
                "result_gross": str(entry.result_gross.amount),
                "costs": str(entry.costs.amount),
                "tax_provisioned": str(entry.tax_provisioned.amount),
                "result_net": str(entry.result_net.amount),
                "strategy": entry.strategy,
                "setup": entry.setup,
                "adherence": entry.adherence,
                "emotional_note": entry.emotional_note,
                "lesson": entry.lesson,
                "source": entry.source,
                "created_at": now,
            },
        )
        await self._session.commit()

        # Journal duplo: JSONL local
        try:
            _append_to_jsonl(entry_id, entry)
        except OSError:
            # Falha no JSONL não deve bloquear a operação principal
            # mas deve ser logada (structlog em Bloco H)
            pass

        return entry_id

    async def get_by_id(self, entry_id: str) -> JournalEntry | None:
        """Retorna um JournalEntry pelo ID, ou None se não encontrado."""
        result = await self._session.execute(
            text(
                """
                SELECT asset, direction, contracts, entry_price, exit_price,
                       result_gross, costs, strategy, setup, adherence,
                       emotional_note, lesson, source
                FROM cam_journal_entries
                WHERE id = :id
                """
            ),
            {"id": entry_id},
        )
        row = result.fetchone()
        if row is None:
            return None

        (
            asset, direction, contracts, entry_price, exit_price,
            result_gross, costs, strategy, setup, adherence,
            emotional_note, lesson, source,
        ) = row

        return JournalEntry(
            asset=asset,
            direction=direction,
            contracts=int(contracts),
            entry_price=Decimal(str(entry_price)),
            exit_price=Decimal(str(exit_price)),
            result_gross=Money(Decimal(str(result_gross))),
            costs=Money(Decimal(str(costs))),
            strategy=strategy,
            setup=setup,
            adherence=adherence,
            emotional_note=emotional_note,
            lesson=lesson,
            source=source or "MANUAL",
        )

    async def list_by_date(self, date: str) -> list[JournalEntry]:
        """Lista JournalEntries de uma data (formato YYYY-MM-DD)."""
        result = await self._session.execute(
            text(
                """
                SELECT asset, direction, contracts, entry_price, exit_price,
                       result_gross, costs, strategy, setup, adherence,
                       emotional_note, lesson, source
                FROM cam_journal_entries
                WHERE DATE(created_at) = :date
                ORDER BY created_at ASC
                """
            ),
            {"date": date},
        )
        rows = result.fetchall()
        return [
            JournalEntry(
                asset=r[0], direction=r[1], contracts=int(r[2]),
                entry_price=Decimal(str(r[3])), exit_price=Decimal(str(r[4])),
                result_gross=Money(Decimal(str(r[5]))),
                costs=Money(Decimal(str(r[6]))),
                strategy=r[7], setup=r[8], adherence=r[9],
                emotional_note=r[10], lesson=r[11],
                source=r[12] or "MANUAL",
            )
            for r in rows
        ]

    async def list_by_strategy(self, strategy: str) -> list[JournalEntry]:
        """Lista JournalEntries por estratégia."""
        result = await self._session.execute(
            text(
                """
                SELECT asset, direction, contracts, entry_price, exit_price,
                       result_gross, costs, strategy, setup, adherence,
                       emotional_note, lesson, source
                FROM cam_journal_entries
                WHERE strategy = :strategy
                ORDER BY created_at DESC
                """
            ),
            {"strategy": strategy},
        )
        rows = result.fetchall()
        return [
            JournalEntry(
                asset=r[0], direction=r[1], contracts=int(r[2]),
                entry_price=Decimal(str(r[3])), exit_price=Decimal(str(r[4])),
                result_gross=Money(Decimal(str(r[5]))),
                costs=Money(Decimal(str(r[6]))),
                strategy=r[7], setup=r[8], adherence=r[9],
                emotional_note=r[10], lesson=r[11],
                source=r[12] or "MANUAL",
            )
            for r in rows
        ]

    async def list_all(self) -> list[JournalEntry]:
        """Lista todos os JournalEntries (para exportação)."""
        result = await self._session.execute(
            text(
                """
                SELECT asset, direction, contracts, entry_price, exit_price,
                       result_gross, costs, strategy, setup, adherence,
                       emotional_note, lesson, source
                FROM cam_journal_entries
                ORDER BY created_at DESC
                """
            )
        )
        rows = result.fetchall()
        return [
            JournalEntry(
                asset=r[0], direction=r[1], contracts=int(r[2]),
                entry_price=Decimal(str(r[3])), exit_price=Decimal(str(r[4])),
                result_gross=Money(Decimal(str(r[5]))),
                costs=Money(Decimal(str(r[6]))),
                strategy=r[7], setup=r[8], adherence=r[9],
                emotional_note=r[10], lesson=r[11],
                source=r[12] or "MANUAL",
            )
            for r in rows
        ]
