"""
Repository da feature kill_switch — SQLAlchemy 2.0 async.

Persiste em cam_kill_switch_events.
get_current_state() deriva o estado a partir do último evento registrado.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam.features.kill_switch.domain import KillSwitchEvent, KillSwitchState


class KillSwitchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_event(self, event: KillSwitchEvent) -> str:
        """Persiste um evento de kill switch. Retorna o UUID gerado."""
        event_id = str(uuid.uuid4())
        await self._session.execute(
            text(
                """
                INSERT INTO cam_kill_switch_events
                    (id, action, reason, created_at)
                VALUES
                    (:id, :action, :reason, :created_at)
                """
            ),
            {
                "id": event_id,
                "action": event.action,
                "reason": event.reason,
                "created_at": datetime.now(UTC),
            },
        )
        await self._session.commit()
        return event_id

    async def get_current_state(self) -> KillSwitchState:
        """
        Retorna o estado atual do kill switch.

        O estado é derivado do último evento registrado:
        - Sem eventos → inativo (padrão seguro)
        - Último evento ACTIVATE → ativo
        - Último evento DEACTIVATE → inativo
        """
        result = await self._session.execute(
            text(
                """
                SELECT action, reason
                FROM cam_kill_switch_events
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
        )
        row = result.fetchone()
        if row is None:
            return KillSwitchState(active=False)

        action, reason = row
        return KillSwitchState(
            active=(action == "ACTIVATE"),
            last_action=action,
            last_reason=reason,
        )
