"""
QA-FIND-SEC-10 — Risk Engine assert_derivative_only (Art. 23).

Defesa estrutural plugada no engine.validate: rejeita candidatos e
open_positions com asset não-derivativo.
"""
from __future__ import annotations

from datetime import time
from decimal import Decimal

import pytest

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    OpenPosition,
    Phase,
)
from cam._shared.risk import OrderCandidate, RiskContext, validate


def _clean_context(open_positions=None) -> RiskContext:
    return RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000")),
        daily_pnl=Money.zero(),
        weekly_pnl=Money.zero(),
        monthly_pnl=Money.zero(),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=open_positions or [],
        current_time=time(11, 30),
    )


def _candidate(asset=AssetType.WIN) -> OrderCandidate:
    return OrderCandidate(
        asset=asset,
        direction=Direction.LONG,
        contracts=ContractCount(1),
        intended_stop_loss_points=Decimal("150"),
        is_setup_a_plus=True,
    )


class TestAssertDerivativeOnly:
    def test_win_accepted_baseline(self):
        decision = validate(_candidate(AssetType.WIN), _clean_context())
        # Pode aprovar ou rejeitar por outro validator, mas NÃO levanta AssertionError
        assert decision is not None

    def test_open_position_with_petr4_raises_assertion(self):
        """
        Se algum caller construir OpenPosition com asset string PETR4
        (burlando o type system), o Risk Engine recusa estruturalmente.
        """
        # Constrói OpenPosition burlando StrEnum (caminho não-tipado)
        bogus = OpenPosition(
            asset=AssetType.WIN,  # type ok mas substituiremos via __dict__
            contracts=ContractCount(1),
            direction=Direction.LONG,
            entry_price=Decimal("100"),
        )
        # Hack para simular caller burlado
        object.__setattr__(bogus, "asset", "PETR4")
        with pytest.raises(AssertionError) as ei:
            validate(_candidate(), _clean_context(open_positions=[bogus]))
        assert "Art. 23" in str(ei.value)

    def test_candidate_with_string_petr4_raises_assertion(self):
        """Caller que serializa candidate via dict pode passar asset string."""
        cand = _candidate()
        object.__setattr__(cand, "asset", "ITUB4")
        with pytest.raises(AssertionError) as ei:
            validate(cand, _clean_context())
        assert "Art. 23" in str(ei.value)
