"""
Tipos de decisão do Risk Engine.

Approved e Rejected são imutáveis (frozen=True) — o engine nunca altera
uma decisão após emiti-la.

Zero I/O — Pure Python.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Approved:
    """Operação aprovada pelo pipeline completo de validators."""

    approved: bool = True


@dataclass(frozen=True)
class Rejected:
    """
    Operação rejeitada por um validator específico.

    reason: descrição legível do motivo da rejeição.
    validator: nome do validator que rejeitou (para logging e auditoria).
    """

    reason: str
    validator: str
    approved: bool = False


RiskDecision = Approved | Rejected
