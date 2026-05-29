"""
T-MT5-C01 — Schemas Pydantic conforme SPEC v0.2 §4.1.
"""
from datetime import datetime, timezone
from decimal import Decimal

import pytest


def test_mt5_tick_serialization():
    from cam.features.mt5_integration.schemas import MT5Tick
    t = MT5Tick(symbol="WIN", bid=Decimal("135000"), ask=Decimal("135005"), last=Decimal("135002"), volume=100, ts_unix_ms=1779000000000)
    assert t.symbol == "WIN"
    assert t.bid == Decimal("135000")


def test_mt5_position_has_pnl_net_always():
    """Art. 25o — pnl_net obrigatorio."""
    from cam.features.mt5_integration.schemas import MT5Position
    p = MT5Position(
        symbol="WIN", contracts=1, direction="LONG",
        entry_price=Decimal("135000"), current_price=Decimal("135100"),
        pnl_gross=Decimal("20"), pnl_net=Decimal("16"),
        opened_at=datetime.now(timezone.utc),
    )
    assert p.pnl_net == Decimal("16")
    # pnl_net e required
    with pytest.raises(Exception):
        MT5Position(symbol="WIN", contracts=1, direction="LONG", entry_price=1, current_price=1, pnl_gross=0, opened_at=datetime.now(timezone.utc))


def test_mt5_bridge_status_states():
    from cam.features.mt5_integration.schemas import MT5BridgeStatus
    s = MT5BridgeStatus(state="ONLINE", last_heartbeat_at=None, last_heartbeat_age_ms=None, avg_latency_ms=None, host="127.0.0.1", pub_port=5556, req_port=5557, mt5_path=None)
    assert s.state == "ONLINE"
    with pytest.raises(Exception):
        MT5BridgeStatus(state="UNKNOWN_STATE", host="127.0.0.1", pub_port=5556, req_port=5557, mt5_path=None)


def test_validate_intention_request_long_short_only():
    from cam.features.mt5_integration.schemas import ValidateIntentionRequest
    r = ValidateIntentionRequest(asset="WIN", direction="LONG", contracts=1, intended_stop_loss_points=Decimal("150"))
    assert r.direction == "LONG"
    with pytest.raises(Exception):
        ValidateIntentionRequest(asset="WIN", direction="BUY", contracts=1, intended_stop_loss_points=Decimal("150"))


def test_validate_intention_request_max_contracts_art11():
    """Art. 11o — 2 contratos absoluto."""
    from cam.features.mt5_integration.schemas import ValidateIntentionRequest
    r = ValidateIntentionRequest(asset="WIN", direction="LONG", contracts=2, intended_stop_loss_points=Decimal("150"))
    assert r.contracts == 2
    with pytest.raises(Exception):
        ValidateIntentionRequest(asset="WIN", direction="LONG", contracts=3, intended_stop_loss_points=Decimal("150"))


def test_import_result_shape():
    from cam.features.mt5_integration.schemas import ImportResult
    r = ImportResult(imported=10, duplicates=2, errors=0)
    assert r.imported == 10
    assert r.duplicates == 2
