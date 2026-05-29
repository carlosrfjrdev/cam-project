"""
ScalingEventsRepository — TASK-052 (BL-H2).

CRUD de `cam_constitutional_scaling_events`. Append-only por design.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ScalingEventsRepository:
    EVENT_TYPES = {
        "ELIGIBILITY_COMPUTED",
        "ELIGIBILITY_READY",
        "PROPOSED",
        "APPROVED",
        "REVOKED",
        "IN_FORCE",
        "AUTO_REVERTED",
        "SOFT_KILL_SWITCH",
        "BLOCKED_ATTEMPT",
    }

    async def insert(
        self,
        session: AsyncSession,
        *,
        event_type: str,
        strategy_id: UUID | None = None,
        proposed_limit_win: int | None = None,
        proposed_limit_wdo: int | None = None,
        evidence_json: dict[str, Any] | None = None,
        cooldown_days: int | None = None,
        notes: str | None = None,
    ) -> UUID:
        if event_type not in self.EVENT_TYPES:
            raise ValueError(f"event_type inválido: {event_type}")
        now = datetime.now(UTC)
        cooldown_ends_at = (
            now + timedelta(days=cooldown_days)
            if cooldown_days is not None
            else None
        )
        result = await session.execute(
            text(
                "INSERT INTO cam_constitutional_scaling_events "
                "(ts, event_type, strategy_id, proposed_limit_win, "
                " proposed_limit_wdo, evidence_json, cooldown_days, "
                " cooldown_ends_at, notes) "
                "VALUES (:ts, :et, :sid, :plw, :plwdo, "
                "        CAST(:ev AS jsonb), :cd, :cea, :notes) "
                "RETURNING id"
            ),
            {
                "ts": now,
                "et": event_type,
                "sid": str(strategy_id) if strategy_id else None,
                "plw": proposed_limit_win,
                "plwdo": proposed_limit_wdo,
                "ev": (
                    json.dumps(evidence_json) if evidence_json else None
                ),
                "cd": cooldown_days,
                "cea": cooldown_ends_at,
                "notes": notes,
            },
        )
        row = result.fetchone()
        await session.commit()
        return UUID(str(row[0]))

    async def latest_in_force(
        self, session: AsyncSession, strategy_id: UUID
    ) -> dict[str, Any] | None:
        """
        Retorna o último evento IN_FORCE para a estratégia (se houver),
        considerando que AUTO_REVERTED/REVOKED posteriores invalidam.
        """
        result = await session.execute(
            text(
                "SELECT id, event_type, proposed_limit_win, "
                "       proposed_limit_wdo, cooldown_ends_at, ts "
                "FROM cam_constitutional_scaling_events "
                "WHERE strategy_id = :sid "
                "  AND event_type IN ('IN_FORCE','AUTO_REVERTED','REVOKED') "
                "ORDER BY ts DESC LIMIT 1"
            ),
            {"sid": str(strategy_id)},
        )
        row = result.fetchone()
        if row is None:
            return None
        d = dict(row._mapping)
        if d["event_type"] != "IN_FORCE":
            return None
        return d
