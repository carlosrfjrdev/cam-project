"""
T-MT5-C04 + T-MT5-C05 — Service orquestrador + eventos.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestEventsExist:
    def test_events_exposed(self):
        from cam.features.mt5_integration import events
        for name in ("MT5BridgeOnline", "MT5BridgeOffline", "MT5FillDetected", "MT5PositionChanged"):
            assert hasattr(events, name), f"Evento {name} ausente em events.py"

    def test_events_are_dataclasses_with_ts(self):
        from dataclasses import is_dataclass
        from cam.features.mt5_integration.events import MT5BridgeOffline
        assert is_dataclass(MT5BridgeOffline)
        inst = MT5BridgeOffline(host="127.0.0.1", port=5557, last_seen_ms=12345)
        assert inst.host == "127.0.0.1"


class TestMT5IntegrationService:
    @pytest.mark.asyncio
    async def test_service_initial_status_offline(self):
        from cam.features.mt5_integration.service import MT5IntegrationService
        svc = MT5IntegrationService(host="127.0.0.1", pub_port=5556, req_port=5557)
        status = svc.get_status()
        assert status.state == "OFFLINE"

    @pytest.mark.asyncio
    async def test_service_status_reflects_bridge_alive(self):
        from cam.features.mt5_integration.service import MT5IntegrationService
        svc = MT5IntegrationService(host="127.0.0.1", pub_port=5556, req_port=5557)
        svc._bridge._record_heartbeat()  # simula heartbeat recebido
        status = svc.get_status()
        assert status.state == "ONLINE"
        assert status.last_heartbeat_age_ms is not None

    @pytest.mark.asyncio
    async def test_service_validate_intention_delegates_to_risk_engine(self):
        """Art. 15o — toda intencao passa pelo Risk Engine."""
        from decimal import Decimal
        from cam._shared.domain.primitives import (
            AssetType, ContractCount, Direction, Money, Phase,
        )
        from cam._shared.risk.context import OrderCandidate, RiskContext
        from cam.features.mt5_integration.service import MT5IntegrationService

        svc = MT5IntegrationService(host="127.0.0.1", pub_port=5556, req_port=5557)
        candidate = OrderCandidate(
            asset=AssetType.WIN,
            direction=Direction.LONG,
            contracts=ContractCount(3),  # viola Art. 11o
            intended_stop_loss_points=Decimal("150"),
        )
        ctx = RiskContext(
            kill_switch_active=False,
            phase=Phase.FASE_1,
            pre_market_checklist_done=True,
            post_market_checklist_done=True,
            tax_compliance_ok=True,
            total_capital=Money(Decimal("5000")),
            daily_pnl=Money(Decimal("0")),
            weekly_pnl=Money(Decimal("0")),
            monthly_pnl=Money(Decimal("0")),
            daily_operations_count=0,
            last_operation_result=None,
            last_operation_contracts=None,
            open_positions=[],
        )
        decision = svc.validate_intention(candidate, ctx)
        assert decision.approved is False  # 3 contratos viola Art. 11o
