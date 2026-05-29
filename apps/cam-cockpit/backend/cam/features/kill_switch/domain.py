"""
Domínio da feature kill_switch — Art. 18º da Constituição.

Kill switch é acionável sem justificar oportunidade perdida.
Desativação requer confirmação explícita do operador.
"""
from dataclasses import dataclass


@dataclass
class KillSwitchState:
    """Estado atual do kill switch."""

    active: bool
    last_action: str | None = None
    last_reason: str | None = None


@dataclass
class KillSwitchEvent:
    """
    Evento de domínio do kill switch.

    action: "ACTIVATE" | "DEACTIVATE"
    reason: motivo da ação (obrigatório em ACTIVATE, vazio em DEACTIVATE)
    """

    action: str
    reason: str
