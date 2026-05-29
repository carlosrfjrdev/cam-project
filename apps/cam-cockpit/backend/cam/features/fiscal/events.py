"""
Eventos publicados pela feature fiscal.

DarfPaid é consumido por harvest/ para recalcular snapshot de buckets.
"""
from dataclasses import dataclass

from cam._shared.events import DomainEvent


@dataclass
class DarfPaid(DomainEvent):
    """Publicado quando uma DARF é marcada como paga."""

    month: str
    value_brl: str


@dataclass
class DarfOverdue(DomainEvent):
    """Publicado quando uma DARF passa a ser OVERDUE."""

    month: str
    due_date: str
