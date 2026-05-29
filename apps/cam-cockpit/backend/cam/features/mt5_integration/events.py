"""
Eventos da feature mt5_integration — SPEC v0.2 §4.3.

Publicados via cam._shared.events.EventBus para outras features consumirem
(notifications, risk_console, journal).
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MT5BridgeOnline:
    """Bridge ZeroMQ conectada — first heartbeat ou recuperacao apos OFFLINE."""
    host: str
    port: int


@dataclass(frozen=True)
class MT5BridgeOffline:
    """Sem heartbeat ha mais que threshold (default 3s)."""
    host: str
    port: int
    last_seen_ms: int


@dataclass(frozen=True)
class MT5PositionChanged:
    """Posicao mudou no MT5 (aberta/fechada/contratos diferentes)."""
    symbol: str
    contracts: int
    direction: str
    entry_price: Decimal
    pnl_net: Decimal
    timestamp: datetime


@dataclass(frozen=True)
class MT5FillDetected:
    """Execucao detectada no MT5 (operador agiu manualmente)."""
    symbol: str
    contracts: int
    direction: str
    price: Decimal
    timestamp: datetime
