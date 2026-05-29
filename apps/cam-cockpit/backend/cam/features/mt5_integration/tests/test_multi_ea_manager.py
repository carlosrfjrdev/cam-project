"""TDD First — TASK-059 (BL-I)."""
from __future__ import annotations

import asyncio

import pytest

from cam.features.mt5_integration.multi_ea_manager import (
    EAEndpoint,
    MultiEAManager,
)


def _ep(ea_id="ea1", port=5557, asset="WIN") -> EAEndpoint:
    return EAEndpoint(
        ea_id=ea_id, pub_port=port - 1, req_port=port, asset=asset,
    )


class TestManager:
    def test_init_requires_at_least_one_endpoint(self):
        with pytest.raises(ValueError):
            MultiEAManager([])

    def test_init_rejects_duplicate_ports(self):
        with pytest.raises(ValueError):
            MultiEAManager([
                _ep("ea1", port=5557),
                _ep("ea2", port=5557),
            ])

    def test_init_rejects_duplicate_ea_ids(self):
        with pytest.raises(ValueError):
            MultiEAManager([
                _ep("ea1", port=5557),
                _ep("ea1", port=5558),
            ])

    def test_two_endpoints_distinct_ports(self):
        mgr = MultiEAManager([
            _ep("ea1", port=5557, asset="WIN"),
            _ep("ea2", port=5558, asset="WDO"),
        ])
        assert len(mgr.endpoints) == 2

    def test_get_endpoint_by_asset(self):
        mgr = MultiEAManager([
            _ep("ea1", port=5557, asset="WIN"),
            _ep("ea2", port=5558, asset="WDO"),
        ])
        win = mgr.get_endpoint_for_asset("WIN")
        wdo = mgr.get_endpoint_for_asset("WDO")
        assert win is not None and win.ea_id == "ea1"
        assert wdo is not None and wdo.ea_id == "ea2"

    def test_online_offline_state(self):
        mgr = MultiEAManager([_ep()])
        assert mgr.is_online("ea1") is False
        mgr.mark_online("ea1")
        assert mgr.is_online("ea1") is True
        mgr.mark_offline("ea1")
        assert mgr.is_online("ea1") is False

    @pytest.mark.asyncio
    async def test_dispatch_serialized_no_concurrency(self):
        mgr = MultiEAManager([_ep()])
        results = []

        async def task(i):
            async def cb():
                # Verifica que entradas no lock são serializadas
                results.append(("start", i))
                await asyncio.sleep(0.01)
                results.append(("end", i))
                return i
            return await mgr.dispatch_serialized(cb)

        await asyncio.gather(task(1), task(2), task(3))
        # Cada par start/end deve estar adjacente
        for i in range(0, len(results), 2):
            assert results[i][0] == "start"
            assert results[i + 1][0] == "end"
            assert results[i][1] == results[i + 1][1]
