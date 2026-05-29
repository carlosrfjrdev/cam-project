"""
Repository da feature checklists — SQLAlchemy 2.0 async.

Persiste em cam_checklist_pre_market e cam_checklist_post_market.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam.features.checklists.domain import PostMarketChecklist, PreMarketChecklist


class ChecklistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_pre_market(self, checklist: PreMarketChecklist) -> str:
        """Persiste checklist pré-mercado. Retorna UUID."""
        import json

        entry_id = str(uuid.uuid4())
        await self._session.execute(
            text(
                """
                INSERT INTO cam_checklist_pre_market
                    (id, date, items, is_complete, created_at)
                VALUES
                    (:id, :date, :items, :is_complete, :created_at)
                ON CONFLICT (date) DO UPDATE SET
                    items = EXCLUDED.items,
                    is_complete = EXCLUDED.is_complete
                """
            ),
            {
                "id": entry_id,
                "date": checklist.date,
                "items": json.dumps(checklist.items),
                "is_complete": checklist.is_complete(),
                "created_at": datetime.now(UTC),
            },
        )
        await self._session.commit()
        return entry_id

    async def save_post_market(self, checklist: PostMarketChecklist) -> str:
        """Persiste checklist pós-mercado. Retorna UUID."""
        import json

        entry_id = str(uuid.uuid4())
        await self._session.execute(
            text(
                """
                INSERT INTO cam_checklist_post_market
                    (id, date, items, is_complete, result_summary, created_at)
                VALUES
                    (:id, :date, :items, :is_complete, :result_summary, :created_at)
                ON CONFLICT (date) DO UPDATE SET
                    items = EXCLUDED.items,
                    is_complete = EXCLUDED.is_complete,
                    result_summary = EXCLUDED.result_summary
                """
            ),
            {
                "id": entry_id,
                "date": checklist.date,
                "items": json.dumps(checklist.items),
                "is_complete": checklist.is_complete(),
                "result_summary": json.dumps(checklist.result_summary)
                if checklist.result_summary
                else None,
                "created_at": datetime.now(UTC),
            },
        )
        await self._session.commit()
        return entry_id

    async def get_pre_market(self, date: str) -> PreMarketChecklist | None:
        """Retorna o checklist pré-mercado de uma data, ou None se não existir."""
        import json

        result = await self._session.execute(
            text(
                "SELECT date, items FROM cam_checklist_pre_market WHERE date = :date"
            ),
            {"date": date},
        )
        row = result.fetchone()
        if row is None:
            return None
        date_val, items_json = row
        return PreMarketChecklist(date=date_val, items=json.loads(items_json))

    async def get_post_market(self, date: str) -> PostMarketChecklist | None:
        """Retorna o checklist pós-mercado de uma data, ou None se não existir."""
        import json

        result = await self._session.execute(
            text(
                """
                SELECT date, items, result_summary
                FROM cam_checklist_post_market
                WHERE date = :date
                """
            ),
            {"date": date},
        )
        row = result.fetchone()
        if row is None:
            return None
        date_val, items_json, summary_json = row
        return PostMarketChecklist(
            date=date_val,
            items=json.loads(items_json),
            result_summary=json.loads(summary_json) if summary_json else None,
        )
