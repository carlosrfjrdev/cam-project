"""TDD First — Fill Subscriber (TASK-029 BL-E)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from cam.features.mt5_integration.fill_subscriber import (
    FillEvent,
    parse_fill,
)


class TestParseFill:
    def test_parses_json_string(self):
        payload = json.dumps(
            {
                "intent_id": str(uuid4()),
                "ticket": 999,
                "asset": "WIN",
                "direction": "LONG",
                "contracts": 1,
                "entry_price": 130000,
                "exit_price": 130150,
                "result_gross": 30.0,
                "fill_ts": "2026-05-27T14:35:00Z",
            }
        )
        event = parse_fill(payload)
        assert isinstance(event, FillEvent)
        assert event.ticket == 999
        assert event.asset == "WIN"
        assert event.direction == "LONG"
        assert event.contracts == 1
        assert event.result_gross == Decimal("30.0")

    def test_parses_dict_directly(self):
        event = parse_fill(
            {
                "intent_id": str(uuid4()),
                "ticket": 1,
                "asset": "WDO",
                "direction": "SHORT",
                "contracts": 2,
                "entry_price": 5500,
                "exit_price": 5450,
                "result_gross": 1000,
                "fill_ts": "2026-05-27T15:00:00Z",
            }
        )
        assert event.asset == "WDO"
        assert event.direction == "SHORT"

    def test_handles_null_exit_price(self):
        event = parse_fill(
            {
                "intent_id": str(uuid4()),
                "ticket": 1,
                "asset": "WIN",
                "direction": "LONG",
                "contracts": 1,
                "entry_price": 130000,
                "exit_price": None,
                "result_gross": None,
                "fill_ts": "2026-05-27T14:00:00Z",
            }
        )
        assert event.exit_price is None
        assert event.result_gross is None
