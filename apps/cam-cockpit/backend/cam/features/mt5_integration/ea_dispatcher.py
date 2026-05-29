"""
EADispatcher — TASK-028 (BL-E SPEC v0.4).

Envia comando `SUBMIT_ORDER` via ZeroMQ REQ/REP ao `cam_bridge.mq5` e aguarda
resposta com timeout 2s. Em produção é o dispatcher padrão do Order Gateway
quando `env in {demo, real}`.

A bridge fica em modo DEMO por design (gate em `cam_bridge.mq5`).
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import zmq
import zmq.asyncio


class BridgeTimeoutError(RuntimeError):
    """Bridge não respondeu em 2s — fail-closed (Art. 18º espírito)."""


class BridgeRejectedError(RuntimeError):
    """Bridge respondeu REJECTED — captura motivo + validator."""


@dataclass
class EADispatcherConfig:
    host: str = "127.0.0.1"
    req_port: int = 5557
    timeout_ms: int = 2000


class EADispatcher:
    """
    Dispatcher real para o EA via ZeroMQ.

    Usado pelo OrderGateway quando env=demo|real e bridge online.

    Pode ser substituído por mock em CI (testes não exigem MT5 ativo).
    """

    def __init__(
        self,
        config: EADispatcherConfig | None = None,
        context: zmq.asyncio.Context | None = None,
    ) -> None:
        self.config = config or EADispatcherConfig()
        self._context = context or zmq.asyncio.Context.instance()

    async def dispatch(
        self,
        candidate: Any,
        idempotency_key: UUID,
    ) -> dict[str, Any]:
        """
        Envia SUBMIT_ORDER e aguarda resposta. Timeout 2s.
        """
        socket = self._context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.config.host}:{self.config.req_port}")
        socket.setsockopt(zmq.LINGER, 0)

        payload = json.dumps(
            {
                "cmd": "SUBMIT_ORDER",
                "asset": candidate.asset.value,
                "direction": candidate.direction.value,
                "contracts": candidate.contracts.value,
                "sl_points": str(candidate.intended_stop_loss_points),
                "idempotency_key": str(idempotency_key),
            }
        )
        try:
            await socket.send_string(payload)
            try:
                raw = await asyncio.wait_for(
                    socket.recv_string(),
                    timeout=self.config.timeout_ms / 1000,
                )
            except TimeoutError as err:
                raise BridgeTimeoutError(
                    "Bridge não respondeu em "
                    f"{self.config.timeout_ms}ms (fail-closed)."
                ) from err
        finally:
            socket.close()

        try:
            response = json.loads(raw)
        except json.JSONDecodeError:
            response = {"raw": raw}

        if response.get("status") == "rejected":
            raise BridgeRejectedError(
                f"EA rejeitou ordem: {response.get('validator')} — "
                f"{response.get('reason')}"
            )
        return response


class MockEADispatcher:
    """Dispatcher offline para testes — produz resposta determinística."""

    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.response = response or {"status": "sent", "ticket": 999, "retcode": 10009}
        self.calls: list[dict[str, Any]] = []

    async def dispatch(
        self, candidate: Any, idempotency_key: UUID
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "candidate": candidate,
                "idempotency_key": str(idempotency_key),
            }
        )
        return self.response
