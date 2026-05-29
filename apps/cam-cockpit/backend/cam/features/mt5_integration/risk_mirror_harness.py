"""
Risk Mirror Harness — TASK-026 (BL-E SPEC v0.4).

Espelha a lógica do `cam_risk_mirror.mq5` em Python para validação de paridade
**sem MT5**. Permite rodar 100+ cenários canônicos em CI sem precisar de Windows.

A versão MQL5 real é o `cam_risk_mirror.mq5` — quando o EA estiver compilado e
rodando em MT5 DEMO, o teste E2E (`test_risk_mirror_parity.py`) também roda contra
o EA real via bridge ZeroMQ.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    Phase,
)
from cam._shared.risk import (
    Approved,
    OrderCandidate,
    Rejected,
    RiskContext,
)
from cam._shared.risk import (
    validate as risk_validate,
)


@dataclass(frozen=True)
class MirrorIntent:
    """Espelha OrderIntent do MQL5."""

    asset: str
    direction: str
    contracts: int
    sl_points: float
    is_setup_a_plus: bool = True


@dataclass(frozen=True)
class MirrorContextSnapshot:
    """Espelha RiskContextSnapshot do MQL5."""

    kill_switch_active: bool = False
    pre_market_checklist_done: bool = True
    post_market_checklist_done: bool = True
    tax_compliance_ok: bool = True
    daily_pnl_pct: float = 0.0
    weekly_pnl_pct: float = 0.0
    monthly_pnl_pct: float = 0.0
    daily_operations_count: int = 0
    open_win_contracts: int = 0
    open_wdo_contracts: int = 0
    phase: int = 1  # 0..4


@dataclass(frozen=True)
class MirrorDecision:
    approved: bool
    validator: str
    reason: str


def evaluate_mirror(intent: MirrorIntent, ctx: MirrorContextSnapshot) -> MirrorDecision:
    """
    Reimplementa `EvaluatePipeline` do MQL5 em Python.

    Resultado deve casar com `risk_validate` em todos os cenários canônicos
    (TASK-026 valida via property-based + fixture set).
    """
    if ctx.kill_switch_active:
        return MirrorDecision(False, "kill_switch_active_check",
                              "Kill switch ativo (Art. 18o)")
    if not ctx.pre_market_checklist_done:
        return MirrorDecision(False, "pre_market_checklist_check",
                              "Checklist pre-mercado nao preenchido (Art. 32o)")
    if not ctx.post_market_checklist_done:
        return MirrorDecision(False, "post_market_checklist_check",
                              "Checklist pos-mercado ausente (Art. 33o)")
    if not ctx.tax_compliance_ok:
        return MirrorDecision(False, "tax_compliance_check",
                              "DARF atrasada (Art. 26o)")
    max_for = 2 if intent.asset == "WIN" else 2  # fallback default 2+2
    open_for = (ctx.open_win_contracts if intent.asset == "WIN"
                else ctx.open_wdo_contracts)
    if open_for + intent.contracts > max_for:
        return MirrorDecision(
            False, "max_contracts_check",
            f"Excede limite (Art. 11): {open_for}+{intent.contracts}>{max_for}",
        )
    if ctx.daily_pnl_pct < -0.03:
        return MirrorDecision(False, "daily_loss_limit_check",
                              "Daily loss limit (Art. 16o)")
    if ctx.weekly_pnl_pct < -0.07:
        return MirrorDecision(False, "weekly_loss_limit_check",
                              "Weekly loss limit (Art. 16o)")
    if ctx.monthly_pnl_pct < -0.15:
        return MirrorDecision(False, "monthly_loss_limit_check",
                              "Monthly loss limit (Art. 16o)")
    if ctx.daily_pnl_pct >= 0.02:
        return MirrorDecision(False, "gain_lock_check",
                              "Gain lock ativado (Art. 17o)")
    ops_limit = 5 if ctx.phase >= 4 else (3 if ctx.phase >= 2 else 99)
    if ctx.daily_operations_count >= ops_limit:
        return MirrorDecision(False, "daily_operations_count_check",
                              "Daily ops limit (Art. 20o)")
    return MirrorDecision(True, "", "")


# ---------------------------------------------------------------------------
# Conversores para chamar o Risk Engine Python real
# ---------------------------------------------------------------------------
_PHASE_MAP = {
    0: Phase.FASE_0,
    1: Phase.FASE_1,
    2: Phase.FASE_2,
    3: Phase.FASE_3,
    4: Phase.FASE_4,
}


def to_python_context(ctx: MirrorContextSnapshot) -> RiskContext:
    from cam._shared.domain.primitives import OpenPosition

    cap = Decimal("5000")
    open_positions = []
    if ctx.open_win_contracts > 0:
        open_positions.append(
            OpenPosition(
                asset=AssetType.WIN,
                contracts=ContractCount(ctx.open_win_contracts),
                direction=Direction.LONG,
                entry_price=Decimal("130000"),
            )
        )
    if ctx.open_wdo_contracts > 0:
        open_positions.append(
            OpenPosition(
                asset=AssetType.WDO,
                contracts=ContractCount(ctx.open_wdo_contracts),
                direction=Direction.LONG,
                entry_price=Decimal("5500"),
            )
        )
    return RiskContext(
        kill_switch_active=ctx.kill_switch_active,
        phase=_PHASE_MAP[ctx.phase],
        pre_market_checklist_done=ctx.pre_market_checklist_done,
        post_market_checklist_done=ctx.post_market_checklist_done,
        tax_compliance_ok=ctx.tax_compliance_ok,
        total_capital=Money(cap),
        daily_pnl=Money(Decimal(str(ctx.daily_pnl_pct)) * cap),
        weekly_pnl=Money(Decimal(str(ctx.weekly_pnl_pct)) * cap),
        monthly_pnl=Money(Decimal(str(ctx.monthly_pnl_pct)) * cap),
        daily_operations_count=ctx.daily_operations_count,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=open_positions,
    )


def to_python_candidate(intent: MirrorIntent) -> OrderCandidate:
    return OrderCandidate(
        asset=AssetType(intent.asset),
        direction=Direction(intent.direction),
        contracts=ContractCount(intent.contracts),
        intended_stop_loss_points=Decimal(str(intent.sl_points)),
        is_setup_a_plus=intent.is_setup_a_plus,
    )


def python_decision_to_mirror(
    candidate: OrderCandidate, context: RiskContext
) -> MirrorDecision:
    """Roda Risk Engine Python e converte para MirrorDecision (paridade)."""
    decision = risk_validate(candidate, context)
    if isinstance(decision, Approved):
        return MirrorDecision(True, "", "")
    assert isinstance(decision, Rejected)
    return MirrorDecision(False, decision.validator, decision.reason)
