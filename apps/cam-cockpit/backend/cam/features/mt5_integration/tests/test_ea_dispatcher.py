"""TDD First — EADispatcher (TASK-028 BL-E)."""
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from cam._shared.domain.primitives import AssetType, ContractCount, Direction
from cam._shared.risk.context import OrderCandidate
from cam.features.mt5_integration.ea_dispatcher import (
    EADispatcherConfig,
    MockEADispatcher,
)


def _candidate() -> OrderCandidate:
    return OrderCandidate(
        asset=AssetType.WIN,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("150"),
    )


class TestMockDispatcher:
    @pytest.mark.asyncio
    async def test_mock_returns_response(self):
        mock = MockEADispatcher()
        result = await mock.dispatch(_candidate(), uuid4())
        assert result["status"] == "sent"
        assert mock.calls
        assert len(mock.calls) == 1

    @pytest.mark.asyncio
    async def test_mock_can_inject_custom_response(self):
        custom = {"status": "rejected", "validator": "kill_switch", "reason": "ks active"}
        mock = MockEADispatcher(response=custom)
        result = await mock.dispatch(_candidate(), uuid4())
        assert result == custom


class TestConfig:
    def test_defaults(self):
        cfg = EADispatcherConfig()
        assert cfg.host == "127.0.0.1"
        assert cfg.req_port == 5557
        assert cfg.timeout_ms == 2000
