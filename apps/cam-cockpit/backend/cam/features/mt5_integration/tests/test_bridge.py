"""
T-MT5-C02 + T-MT5-C03 — Bridge ZeroMQ cliente + assert read-only.

Os testes nao requerem MT5/Wine — usam mock do socket ZeroMQ.
"""
import asyncio
import inspect
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBridgeReadOnlyAssert:
    """CA15.2 — bridge.py NAO PODE expor send_order ou similar."""

    def test_module_has_no_send_order_attribute(self):
        from cam.features.mt5_integration import bridge
        forbidden = {"send_order", "place_order", "open_position", "close_position", "modify_order"}
        attrs = set(dir(bridge))
        intersection = attrs & forbidden
        assert not intersection, f"Atributos proibidos detectados (read-only v0.2): {intersection}"

    def test_source_has_no_order_send_calls(self):
        """Procura padrao de CHAMADA (com parenteses) — exclui literais em listas."""
        from cam.features.mt5_integration import bridge
        source = inspect.getsource(bridge)
        forbidden_calls = ["OrderSend(", "OrderClose(", "PositionOpen(", "PositionClose(", "OrderModify("]
        for call in forbidden_calls:
            assert call not in source, f"Chamada proibida {call!r} no source de bridge.py"


class TestBridgeClient:
    @pytest.mark.asyncio
    async def test_initial_state_offline(self):
        from cam.features.mt5_integration.bridge import MT5BridgeClient
        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557)
        assert client.is_alive() is False
        assert client.last_heartbeat_age_ms is None

    @pytest.mark.asyncio
    async def test_records_heartbeat(self):
        from cam.features.mt5_integration.bridge import MT5BridgeClient
        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557)
        client._record_heartbeat()
        assert client.is_alive() is True
        assert client.last_heartbeat_age_ms is not None
        assert client.last_heartbeat_age_ms < 1000  # < 1s acabou de marcar

    @pytest.mark.asyncio
    async def test_heartbeat_expires_after_threshold(self):
        from cam.features.mt5_integration.bridge import MT5BridgeClient
        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557, heartbeat_timeout_ms=100)
        client._record_heartbeat()
        await asyncio.sleep(0.2)
        assert client.is_alive() is False

    @pytest.mark.asyncio
    async def test_request_returns_dict_with_mock(self):
        from cam.features.mt5_integration.bridge import MT5BridgeClient

        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557)
        # mock interno do socket REQ — zmq.asyncio: send_json e recv_json sao awaitable
        mock_socket = MagicMock()
        mock_socket.send_json = AsyncMock()
        mock_socket.recv_json = AsyncMock(return_value={"status": "ok", "data": {"balance": 5000}})
        client._req_socket = mock_socket

        result = await client.request("GET_STATE")
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_request_rejects_unauthorized_command(self):
        """CA15.3 — comando fora da whitelist e bloqueado."""
        from cam.features.mt5_integration.bridge import MT5BridgeClient
        client = MT5BridgeClient(host="127.0.0.1", pub_port=5556, req_port=5557)
        result = await client.request("SEND_ORDER")
        assert result["error"] == "UNAUTHORIZED_COMMAND"
        assert result["cmd"] == "SEND_ORDER"
