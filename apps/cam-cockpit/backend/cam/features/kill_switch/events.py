"""
Eventos publicados pela feature kill_switch.

KillSwitchActivated e KillSwitchDeactivated são consumidos por:
- notifications/ (Telegram alert)
- Audit trail (structlog)
"""
from dataclasses import dataclass

from cam._shared.events import DomainEvent


@dataclass
class KillSwitchActivated(DomainEvent):
    """Publicado quando o kill switch é ativado. Art. 18º."""

    reason: str


@dataclass
class KillSwitchDeactivated(DomainEvent):
    """Publicado quando o kill switch é desativado com confirmação explícita."""

    pass
