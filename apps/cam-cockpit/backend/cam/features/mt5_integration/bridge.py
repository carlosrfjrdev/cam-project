"""
Bridge ZeroMQ Python <-> EA MQL5 — READ-ONLY em v0.2.

CA15.1: bridge NAO PODE enviar ordens. Verificacao via teste de inspecao do
modulo (test_bridge.py::TestBridgeReadOnlyAssert).

SPEC v0.2.1:
- R12.01 a R12.06 — bridge ZeroMQ obrigatoria
- R14 — EA cam_bridge.mq5 publica via PUB e responde REQ/REP read-only
- R16 — heartbeat 1s, threshold 3s, modo degradado seguro

Padroes ZeroMQ:
- SUB: client.subscribe(topic, handler) recebe ticks/posicoes/fills/heartbeat
- REQ: client.request("PING") -> "PONG"
"""
import asyncio
import time
from typing import Any, Awaitable, Callable

import zmq
import zmq.asyncio

DEFAULT_HEARTBEAT_TIMEOUT_MS = 3000  # R12.04 — > 3s sem heartbeat = offline
REQ_TIMEOUT_MS = 1500


class MT5BridgeClient:
    """
    Cliente ZeroMQ assincrono para a bridge MT5 (EA cam_bridge.mq5).

    Read-only em v0.2 — nao expoe send_order, OrderSend, etc.

    Usage:
        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557)
        await client.connect()
        state = await client.request("GET_STATE")
        await client.subscribe("mt5.tick", on_tick_handler)
        ...
        await client.disconnect()
    """

    def __init__(
        self,
        host: str,
        pub_port: int,
        req_port: int,
        heartbeat_timeout_ms: int = DEFAULT_HEARTBEAT_TIMEOUT_MS,
    ) -> None:
        self.host = host
        self.pub_port = pub_port
        self.req_port = req_port
        self.heartbeat_timeout_ms = heartbeat_timeout_ms

        self._context: zmq.asyncio.Context | None = None
        self._sub_socket: Any = None
        self._req_socket: Any = None
        self._last_heartbeat_ts: float | None = None
        self._latency_samples: list[float] = []
        self._subscribers: dict[str, list[Callable[[bytes], Awaitable[None]]]] = {}
        self._sub_task: asyncio.Task | None = None

    # ---------------------- Lifecycle ----------------------

    async def connect(self) -> None:
        """Inicializa sockets PUB/SUB e REQ/REP."""
        self._context = zmq.asyncio.Context.instance()
        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.connect(f"tcp://{self.host}:{self.pub_port}")
        self._sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        self._req_socket = self._context.socket(zmq.REQ)
        self._req_socket.setsockopt(zmq.RCVTIMEO, REQ_TIMEOUT_MS)
        self._req_socket.setsockopt(zmq.SNDTIMEO, REQ_TIMEOUT_MS)
        self._req_socket.connect(f"tcp://{self.host}:{self.req_port}")

        self._sub_task = asyncio.create_task(self._sub_loop())

    async def disconnect(self) -> None:
        if self._sub_task:
            self._sub_task.cancel()
            try:
                await self._sub_task
            except asyncio.CancelledError:
                pass
            self._sub_task = None
        if self._sub_socket is not None:
            self._sub_socket.close()
            self._sub_socket = None
        if self._req_socket is not None:
            self._req_socket.close()
            self._req_socket = None

    # ---------------------- Heartbeat ----------------------

    def _record_heartbeat(self) -> None:
        self._last_heartbeat_ts = time.time()

    def is_alive(self) -> bool:
        """True quando heartbeat foi recebido dentro do threshold."""
        if self._last_heartbeat_ts is None:
            return False
        age_ms = (time.time() - self._last_heartbeat_ts) * 1000
        return age_ms < self.heartbeat_timeout_ms

    @property
    def last_heartbeat_age_ms(self) -> int | None:
        if self._last_heartbeat_ts is None:
            return None
        return int((time.time() - self._last_heartbeat_ts) * 1000)

    @property
    def avg_latency_ms(self) -> float | None:
        if not self._latency_samples:
            return None
        return sum(self._latency_samples) / len(self._latency_samples)

    # ---------------------- REQ/REP ----------------------

    async def request(self, cmd: str, **params: Any) -> dict:
        """Envia comando read-only e aguarda resposta do EA."""
        if cmd not in {"GET_STATE", "GET_POSITIONS", "GET_SYMBOL_INFO", "PING"}:
            return {"error": "UNAUTHORIZED_COMMAND", "cmd": cmd}
        if self._req_socket is None:
            raise RuntimeError("Bridge nao conectada — chame connect() primeiro")

        payload = {"cmd": cmd, **params}
        t0 = time.time()
        # send_json/recv_json: em zmq.asyncio, send_json e sync mas recv_json e awaitable
        await self._req_socket.send_json(payload)
        response = await self._req_socket.recv_json()
        latency = (time.time() - t0) * 1000
        self._latency_samples.append(latency)
        if len(self._latency_samples) > 50:
            self._latency_samples.pop(0)
        return response

    # ---------------------- PUB/SUB ----------------------

    async def subscribe(self, topic: str, handler: Callable[[bytes], Awaitable[None]]) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    async def _sub_loop(self) -> None:
        if self._sub_socket is None:
            return
        try:
            while True:
                msg = await self._sub_socket.recv_multipart()
                if not msg:
                    continue
                topic = msg[0].decode("utf-8", errors="replace")
                payload = msg[1] if len(msg) > 1 else b""
                if topic == "mt5.heartbeat":
                    self._record_heartbeat()
                for handler in self._subscribers.get(topic, []):
                    try:
                        await handler(payload)
                    except Exception:
                        # nao propaga — handler com bug nao deve derrubar a bridge
                        pass
        except asyncio.CancelledError:
            raise
        except Exception:
            # erro de socket — bridge cai para OFFLINE via heartbeat expiration
            pass
