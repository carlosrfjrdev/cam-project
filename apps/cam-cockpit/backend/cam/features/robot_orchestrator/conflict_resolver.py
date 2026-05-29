"""
Conflict Resolver — TASK-044 (BL-H1).

Implementa POV §3.11 (Resolução de Conflitos) com 6 cenários determinísticos:

  - Mesma direção/mesmo ativo → vence maior expectância 30d.
  - Direção oposta/mesmo ativo → ambos rejeitados (DIRECTIONAL_CONFLICT).
  - Empate de expectância dentro de 5% → ambos rejeitados (AMBIGUOUS_TIE).
  - Ativos diferentes → ambos seguem para aggregate_risk_check.
  - Estratégia individual suspensa → skip antes do resolver.
  - 1 só candidato → passa direto.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from cam._shared.domain.primitives import AssetType, Direction


class ConflictReason(StrEnum):
    NONE = "none"
    DIRECTIONAL_CONFLICT = "DIRECTIONAL_CONFLICT"
    AMBIGUOUS_TIE = "AMBIGUOUS_TIE"
    SUSPENDED = "SUSPENDED"


@dataclass(frozen=True)
class ResolverCandidate:
    """Candidato vindo de uma estratégia individual."""

    strategy_id: UUID
    asset: AssetType
    direction: Direction
    contracts: int
    expectancy_30d: Decimal  # esperança líquida em BRL nos últimos 30 dias
    is_suspended: bool = False


@dataclass
class ResolutionResult:
    winners: list[ResolverCandidate] = field(default_factory=list)
    rejected: list[ResolverCandidate] = field(default_factory=list)
    audits: list[tuple[str, str]] = field(default_factory=list)


def resolve(
    candidates: list[ResolverCandidate],
) -> ResolutionResult:
    """
    Aplica POV §3.11. Determinístico.
    """
    result = ResolutionResult()

    # 1) Suspended → skip
    active = [c for c in candidates if not c.is_suspended]
    for c in candidates:
        if c.is_suspended:
            result.rejected.append(c)
            result.audits.append((str(c.strategy_id), ConflictReason.SUSPENDED.value))

    if len(active) == 0:
        return result
    if len(active) == 1:
        result.winners.extend(active)
        return result

    # Agrupar por (asset, direction)
    by_asset: dict[AssetType, list[ResolverCandidate]] = {}
    for c in active:
        by_asset.setdefault(c.asset, []).append(c)

    for _asset, group in by_asset.items():
        if len(group) == 1:
            result.winners.append(group[0])
            continue
        # Mesma direção?
        directions = {c.direction for c in group}
        if len(directions) == 1:
            # Mesma direção/mesmo ativo → maior expectância 30d vence.
            sorted_group = sorted(
                group, key=lambda c: c.expectancy_30d, reverse=True
            )
            top = sorted_group[0]
            runner = sorted_group[1]
            # Empate (dentro de 5%)?
            if runner.expectancy_30d > 0 and (
                (top.expectancy_30d - runner.expectancy_30d)
                / abs(runner.expectancy_30d)
            ) < Decimal("0.05"):
                for c in group:
                    result.rejected.append(c)
                    result.audits.append(
                        (str(c.strategy_id), ConflictReason.AMBIGUOUS_TIE.value)
                    )
            else:
                result.winners.append(top)
                for c in sorted_group[1:]:
                    result.rejected.append(c)
                    result.audits.append(
                        (str(c.strategy_id),
                         f"LOST_TO_{top.strategy_id}")
                    )
        else:
            # Direção oposta/mesmo ativo → DIRECTIONAL_CONFLICT
            for c in group:
                result.rejected.append(c)
                result.audits.append(
                    (str(c.strategy_id), ConflictReason.DIRECTIONAL_CONFLICT.value)
                )

    return result
