"""
T-TD-001 — Novo validator total_open_contracts_check (Art. 12o explicito).

TDD First: define comportamento esperado antes da implementacao.

Cenario: Carlos tem 1 WIN aberto e tenta abrir outro WIN.
- Fase 1/2: limite = 1 contrato — soma 2 → REJEITA (mesmo asset).
- Fase 3/4: limite = 2 contratos — soma 2 → APROVA (no limite).
- Fase 3/4: soma 3 → REJEITA.
"""
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
from cam._shared.risk.context import OrderCandidate, RiskContext


def _ctx(phase: Phase, open_positions: list[OpenPosition]) -> RiskContext:
    return RiskContext(
        kill_switch_active=False,
        phase=phase,
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
        open_positions=open_positions,
    )


def _candidate(asset: AssetType, contracts: int) -> OrderCandidate:
    return OrderCandidate(
        asset=asset,
        direction=Direction.LONG,
        contracts=ContractCount(contracts),
        intended_stop_loss_points=Decimal("150"),
    )


def _open_pos(asset: AssetType, contracts: int) -> OpenPosition:
    return OpenPosition(
        asset=asset,
        contracts=ContractCount(contracts),
        direction=Direction.LONG,
        entry_price=Decimal("135000"),
    )


class TestTotalOpenContractsCheck:
    def test_no_open_positions_passes(self):
        from cam._shared.risk.validators.group2_limits import total_open_contracts_check
        decision = total_open_contracts_check(_candidate(AssetType.WIN, 1), _ctx(Phase.FASE_2, []))
        assert decision.approved is True

    def test_phase2_one_open_win_plus_one_more_rejects(self):
        """Carlos ja tem 1 WIN aberto + tenta abrir outro WIN em Fase 2 → REJEITA."""
        from cam._shared.risk.validators.group2_limits import total_open_contracts_check
        decision = total_open_contracts_check(
            _candidate(AssetType.WIN, 1),
            _ctx(Phase.FASE_2, [_open_pos(AssetType.WIN, 1)]),
        )
        assert decision.approved is False
        assert "total" in decision.reason.lower() or "soma" in decision.reason.lower()

    def test_phase3_one_open_win_plus_one_more_approves(self):
        """Fase 3 — limite 2 — soma 2 → APROVA."""
        from cam._shared.risk.validators.group2_limits import total_open_contracts_check
        decision = total_open_contracts_check(
            _candidate(AssetType.WIN, 1),
            _ctx(Phase.FASE_3, [_open_pos(AssetType.WIN, 1)]),
        )
        assert decision.approved is True

    def test_phase3_two_open_win_plus_one_more_rejects(self):
        """Fase 3 — 2 abertas + 1 nova = 3 → REJEITA."""
        from cam._shared.risk.validators.group2_limits import total_open_contracts_check
        decision = total_open_contracts_check(
            _candidate(AssetType.WIN, 1),
            _ctx(Phase.FASE_3, [_open_pos(AssetType.WIN, 2)]),
        )
        assert decision.approved is False

    def test_different_asset_does_not_count(self):
        """Open WDO nao conta para limite de WIN."""
        from cam._shared.risk.validators.group2_limits import total_open_contracts_check
        decision = total_open_contracts_check(
            _candidate(AssetType.WIN, 1),
            _ctx(Phase.FASE_2, [_open_pos(AssetType.WDO, 1)]),
        )
        assert decision.approved is True

    def test_in_pipeline(self):
        """Validator inserido entre simultaneous_position e Grupo 3."""
        from cam._shared.risk.engine import _VALIDATORS
        names = [v.__name__ for v in _VALIDATORS]
        assert "total_open_contracts_check" in names
        idx_simul = names.index("simultaneous_position_check")
        idx_total = names.index("total_open_contracts_check")
        idx_daily_pnl = names.index("daily_loss_limit_check")
        assert idx_simul < idx_total < idx_daily_pnl
