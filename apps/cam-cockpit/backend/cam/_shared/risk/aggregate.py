"""
Aggregate Risk Check — TASK-045 (BL-H1 SPEC v0.4).

Validator agregado (Art. 11-A). Posição 8.6 do pipeline do Risk Engine.
Soma de contratos por ativo respeita Art. 11º **lendo o limite vigente** via
`get_current_limits()` (T047) — nunca constants hardcoded.

Adicionais (Art. 11-A):
  - Suspende estratégia individual com aderência < 95% (R8.02 item 7).
  - Bloqueia ativação de N+1ª estratégia com correlação > 0.7 (R8.02 item 8).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from cam._shared.domain.primitives import AssetType
from cam._shared.risk.decision import Approved, Rejected, RiskDecision
from cam._shared.risk.limits import get_current_limits


@dataclass(frozen=True)
class AggregateCandidate:
    """Candidato agregado por estratégia."""

    strategy_id: str
    asset: AssetType
    contracts: int
    adherence: Decimal
    is_suspended: bool = False


@dataclass(frozen=True)
class AggregateContext:
    """Contexto agregado: lista de open por ativo + correlações pré-computadas."""

    open_win_contracts: int = 0
    open_wdo_contracts: int = 0
    strategy_adherence: dict[str, Decimal] | None = None
    # correlations[(strategy_a, strategy_b)] = float
    correlations: dict[tuple[str, str], float] | None = None


# Thresholds canônicos (Art. 11-A)
ADHERENCE_MIN = Decimal("0.95")
CORRELATION_MAX = 0.7


def aggregate_risk_check(
    candidates: list[AggregateCandidate],
    context: AggregateContext,
) -> RiskDecision:
    """
    Valida soma de contratos vs limite vigente (Art. 11-A item a) + aderência
    individual (item 7) + correlação entre estratégias (item 8).

    Estratégia individual suspensa OU aderência < 95% → reject específico.
    Soma de contratos > limite vigente → reject `max_contracts_aggregate`.
    """
    limits = get_current_limits()

    # 1) Suspensão por aderência
    if context.strategy_adherence:
        for c in candidates:
            adh = context.strategy_adherence.get(c.strategy_id)
            if adh is not None and adh < ADHERENCE_MIN:
                return Rejected(
                    reason=(
                        f"Estratégia {c.strategy_id} com aderência "
                        f"{adh} < {ADHERENCE_MIN}. Suspensão Art. 11-A item 7."
                    ),
                    validator="aggregate_risk_check.adherence",
                )

    # 2) Correlação > 0.7 entre estratégias ativas
    if context.correlations:
        for c in candidates:
            for c2 in candidates:
                if c.strategy_id >= c2.strategy_id:
                    continue
                key = (c.strategy_id, c2.strategy_id)
                corr = context.correlations.get(key) or context.correlations.get(
                    (c2.strategy_id, c.strategy_id)
                )
                if corr is not None and corr > CORRELATION_MAX:
                    return Rejected(
                        reason=(
                            f"Correlação {corr:.3f} entre {c.strategy_id} e "
                            f"{c2.strategy_id} > {CORRELATION_MAX}. Art. 11-A item 8."
                        ),
                        validator="aggregate_risk_check.correlation",
                    )

    # 3) Soma de contratos por ativo
    win_sum = sum(c.contracts for c in candidates if c.asset is AssetType.WIN)
    wdo_sum = sum(c.contracts for c in candidates if c.asset is AssetType.WDO)

    if context.open_win_contracts + win_sum > limits.max_win:
        return Rejected(
            reason=(
                f"Soma de WIN ({context.open_win_contracts} abertos + "
                f"{win_sum} candidatos) excede limite vigente "
                f"{limits.max_win} (source={limits.source})."
            ),
            validator="aggregate_risk_check.max_win",
        )
    if context.open_wdo_contracts + wdo_sum > limits.max_wdo:
        return Rejected(
            reason=(
                f"Soma de WDO ({context.open_wdo_contracts} abertos + "
                f"{wdo_sum} candidatos) excede limite vigente "
                f"{limits.max_wdo}."
            ),
            validator="aggregate_risk_check.max_wdo",
        )

    return Approved()
