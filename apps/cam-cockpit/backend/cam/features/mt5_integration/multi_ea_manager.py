"""
Multi-EA Manager — TASK-059 (BL-I SPEC v0.4).

Orquestra múltiplas conexões ZeroMQ a EAs distintos (`cam_bridge.mq5` v2).
Mutex de execução: cada EA publica tick em canal próprio, mas Order Gateway
processa em série via `asyncio.Lock`.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EAEndpoint:
    ea_id: str
    pub_port: int
    req_port: int
    asset: str  # WIN | WDO | ...


@dataclass
class MultiEAManagerState:
    online: set[str] = field(default_factory=set)
    last_heartbeat: dict[str, float] = field(default_factory=dict)


class MultiEAManager:
    """
    Gerencia N EAs. Cada EA tem `ea_id`, porta REQ/REP única e canal PUB
    distinto. Order Gateway usa este manager para escolher EA por asset.
    """

    def __init__(self, endpoints: list[EAEndpoint]) -> None:
        if not endpoints:
            raise ValueError("MultiEAManager exige ≥ 1 endpoint")
        port_set = {e.req_port for e in endpoints}
        if len(port_set) != len(endpoints):
            raise ValueError("Endpoints com portas REP duplicadas")
        ea_ids = {e.ea_id for e in endpoints}
        if len(ea_ids) != len(endpoints):
            raise ValueError("Endpoints com EA_ID duplicados")
        self.endpoints = {e.ea_id: e for e in endpoints}
        self.state = MultiEAManagerState()
        self._lock = asyncio.Lock()

    def get_endpoint_for_asset(self, asset: str) -> EAEndpoint | None:
        """Retorna primeiro endpoint cuja `asset` casa (estratégia simples)."""
        for ep in self.endpoints.values():
            if ep.asset.upper() == asset.upper():
                return ep
        return None

    def mark_online(self, ea_id: str) -> None:
        self.state.online.add(ea_id)

    def mark_offline(self, ea_id: str) -> None:
        self.state.online.discard(ea_id)

    def is_online(self, ea_id: str) -> bool:
        return ea_id in self.state.online

    async def dispatch_serialized(self, callback) -> Any:
        """Executa callback sob mutex (Order Gateway invariante)."""
        async with self._lock:
            return await callback()
