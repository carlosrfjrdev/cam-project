"""
Testes TDD do Bloco D — T-D01.
Cobre F1: validação de intenção via Risk Engine (sem envio de ordem).
"""
import inspect
from decimal import Decimal
from unittest.mock import MagicMock

import pytest


class TestProfitIntegrationF1:
    @pytest.mark.asyncio
    async def test_validate_intention_approved(self):
        from cam._shared.risk import Approved
        from cam.features.profit_integration.service import ProfitIntegrationService

        risk_engine = MagicMock()
        risk_engine.validate = MagicMock(return_value=Approved())
        svc = ProfitIntegrationService(risk_engine=risk_engine)
        result = await svc.validate_intention(
            asset="WIN",
            direction="LONG",
            contracts=1,
            intended_stop_points=Decimal("200"),
            risk_context_builder=MagicMock(return_value=MagicMock()),
        )
        assert result["decision"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_validate_intention_rejected(self):
        from cam._shared.risk import Rejected
        from cam.features.profit_integration.service import ProfitIntegrationService

        risk_engine = MagicMock()
        risk_engine.validate = MagicMock(
            return_value=Rejected(
                reason="Kill switch ativo", validator="kill_switch_active_check"
            )
        )
        svc = ProfitIntegrationService(risk_engine=risk_engine)
        result = await svc.validate_intention(
            asset="WIN",
            direction="LONG",
            contracts=1,
            intended_stop_points=Decimal("200"),
            risk_context_builder=MagicMock(return_value=MagicMock()),
        )
        assert result["decision"] == "REJECTED"
        assert "kill_switch" in result["validator"]

    def test_no_order_sending_code_exists(self):
        """F1 é manual — nenhum código de envio de ordem deve existir (Art. 35º)."""
        from cam.features.profit_integration import service

        source = inspect.getsource(service)
        assert "send_order" not in source.lower()
        assert "place_order" not in source.lower()
        assert "submit" not in source.lower()

    @pytest.mark.asyncio
    async def test_validate_intention_returns_reason_on_rejection(self):
        from cam._shared.risk import Rejected
        from cam.features.profit_integration.service import ProfitIntegrationService

        risk_engine = MagicMock()
        risk_engine.validate = MagicMock(
            return_value=Rejected(
                reason="Limite de contratos excedido", validator="contract_limit_check"
            )
        )
        svc = ProfitIntegrationService(risk_engine=risk_engine)
        result = await svc.validate_intention(
            asset="WIN",
            direction="LONG",
            contracts=3,
            intended_stop_points=Decimal("200"),
            risk_context_builder=MagicMock(return_value=MagicMock()),
        )
        assert result["decision"] == "REJECTED"
        assert result["reason"] == "Limite de contratos excedido"

    @pytest.mark.asyncio
    async def test_approved_result_has_no_reason(self):
        from cam._shared.risk import Approved
        from cam.features.profit_integration.service import ProfitIntegrationService

        risk_engine = MagicMock()
        risk_engine.validate = MagicMock(return_value=Approved())
        svc = ProfitIntegrationService(risk_engine=risk_engine)
        result = await svc.validate_intention(
            asset="WDO",
            direction="SHORT",
            contracts=1,
            intended_stop_points=Decimal("50"),
            risk_context_builder=MagicMock(return_value=MagicMock()),
        )
        assert result["decision"] == "APPROVED"
        assert result["reason"] is None
        assert result["validator"] is None
