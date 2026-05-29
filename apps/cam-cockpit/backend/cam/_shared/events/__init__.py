"""
Event Bus interno do CaM — baseado em asyncio.Queue.

Implementação intencional: asyncio.Queue é suficiente para 1 operador local.
Redis é alternativa documentada (DAS §9 Não-Decisões) para carga real maior.

Não-Decisão: sem persistência de eventos.
Reinício do backend = eventos pendentes perdidos.
Aceitável em Fase 0. Revisitar em Fase 1 se problema real aparecer.
"""
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass
class DomainEvent:
    """Base para todos os eventos de domínio do CaM."""

    pass


class EventBus:
    """
    Bus de eventos in-process baseado em asyncio.Queue.

    Uso:
        bus = EventBus()
        bus.subscribe(MeuEvento, handler_async)
        await bus.publish(MeuEvento())
        await bus.dispatch_all()
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[..., Awaitable[None]]]] = {}
        self._queue: asyncio.Queue[DomainEvent] = asyncio.Queue()

    def subscribe(
        self,
        event_type: type,
        handler: Callable[..., Awaitable[None]],
    ) -> None:
        """Registra um handler assíncrono para um tipo de evento."""
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Enfileira um evento para despacho."""
        await self._queue.put(event)

    async def dispatch_all(self) -> None:
        """Despacha todos os eventos pendentes na fila."""
        while not self._queue.empty():
            event = await self._queue.get()
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                await handler(event)

    def clear(self) -> None:
        """Remove todos os eventos pendentes. Útil em testes."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break


# Instância singleton — compartilhada em runtime via DI no lifespan da API
event_bus = EventBus()
