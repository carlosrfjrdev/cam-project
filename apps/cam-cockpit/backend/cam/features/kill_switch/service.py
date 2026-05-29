"""
Service da feature kill_switch — lógica de aplicação.

Orquestra domain + repository + events.
Desativação requer confirm=True explícito (Art. 18º — sem auto-reversão acidental).
"""
from cam._shared.audit.logger import (
    log_kill_switch_activated,
    log_kill_switch_deactivated,
)
from cam._shared.events import event_bus
from cam.features.kill_switch.domain import KillSwitchEvent
from cam.features.kill_switch.events import KillSwitchActivated, KillSwitchDeactivated


class KillSwitchService:
    def __init__(self, repo: object) -> None:
        self.repo = repo

    async def activate(self, reason: str) -> None:
        """
        Ativa o kill switch.

        Persiste o evento e publica KillSwitchActivated no EventBus.
        Pode ser acionado sem justificar oportunidade perdida (Art. 18º).
        """
        event = KillSwitchEvent(action="ACTIVATE", reason=reason)
        await self.repo.save_event(event)
        # T-TD-027 (SPEC v0.3) — audit trail
        log_kill_switch_activated(reason=reason)
        await event_bus.publish(KillSwitchActivated(reason=reason))

    async def deactivate(self, confirm: bool) -> None:
        """
        Desativa o kill switch.

        Requer confirm=True explícito — sem esse campo, levanta ValueError.
        Proteção contra desativação acidental (Art. 18º).
        """
        if not confirm:
            raise ValueError(
                "Desativação do kill switch requer confirm=True explícito. "
                "Envie {'confirm': true} para confirmar a desativação."
            )
        event = KillSwitchEvent(action="DEACTIVATE", reason="")
        await self.repo.save_event(event)
        # T-TD-027 (SPEC v0.3) — audit trail
        log_kill_switch_deactivated()
        await event_bus.publish(KillSwitchDeactivated())

    async def is_active(self) -> bool:
        """Retorna True se o kill switch está atualmente ativo."""
        state = await self.repo.get_current_state()
        return state.active

    async def get_status(self) -> object:
        """Retorna o estado completo do kill switch (para o endpoint de status)."""
        return await self.repo.get_current_state()
