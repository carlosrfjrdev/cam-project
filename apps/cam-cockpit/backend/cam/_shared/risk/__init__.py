"""
Risk Engine — Shared Kernel do CaM.

Ponto de entrada público. Features importam daqui::

    from cam._shared.risk import (
        validate, OrderCandidate, RiskContext, Approved, Rejected
    )

O engine é Pure Python — Zero I/O. Ver engine.py para detalhes.
"""
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, Rejected, RiskDecision
from cam._shared.risk.engine import validate

__all__ = [
    "validate",
    "OrderCandidate",
    "RiskContext",
    "RiskDecision",
    "Approved",
    "Rejected",
]
