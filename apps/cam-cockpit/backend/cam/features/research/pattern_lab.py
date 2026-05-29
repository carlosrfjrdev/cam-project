"""
Pattern Lab — TASK-038 (BL-G SPEC v0.4).

Busca padrões estatísticos simples (sem ML quant). Por design:
  - Sem sklearn/torch (Out — sklearn é tech-debt v0.5+).
  - Apenas estatística clássica (z-score, regressão linear simples, etc.).

Exemplo de padrão suportado: "queda ≥ X% em N ativos consecutivos puxa Y no
dia seguinte".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class PatternSpec:
    """Especificação declarativa de padrão a buscar."""

    name: str
    description: str
    trigger_assets: list[str]
    target_asset: str
    trigger_pct: Decimal  # ex.: -0.01 = queda ≥ 1%
    target_pct: Decimal   # ex.: 0.005 = alta ≥ 0.5% no dia seguinte
    horizon_days: int = 1


@dataclass
class PatternMatch:
    pattern: PatternSpec
    occurred_on: date
    next_day_return: float
    triggered: bool


@dataclass
class PatternSearchResult:
    pattern: PatternSpec
    matches: list[PatternMatch] = field(default_factory=list)
    p_value: float = 1.0  # placeholder; teste binomial simplificado.

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern": self.pattern.name,
            "matches": len(self.matches),
            "p_value": self.p_value,
        }


def search_patterns(
    spec: PatternSpec,
    series_by_asset: dict[str, list[tuple[date, Decimal]]],
    *,
    min_occurrences: int = 5,
) -> PatternSearchResult:
    """
    Procura ocorrências do padrão e retorna `PatternSearchResult`.

    Implementação intencionalmente simples: para cada dia, verifica se TODOS
    os trigger_assets caíram ≥ trigger_pct; depois mede retorno do target
    no dia seguinte.
    """
    result = PatternSearchResult(pattern=spec)
    target_series = series_by_asset.get(spec.target_asset)
    if not target_series:
        return result

    # Map date → return (close-to-close)
    def returns(series: list[tuple[date, Decimal]]) -> dict[date, float]:
        out: dict[date, float] = {}
        for i in range(1, len(series)):
            prev_d, prev_p = series[i - 1]
            curr_d, curr_p = series[i]
            try:
                out[curr_d] = (float(curr_p) - float(prev_p)) / float(prev_p)
            except ZeroDivisionError:
                continue
        return out

    target_returns = returns(target_series)
    triggers_returns = {
        a: returns(series_by_asset[a])
        for a in spec.trigger_assets
        if a in series_by_asset
    }
    if not triggers_returns:
        return result

    # Conjunto de datas comuns
    common_dates = set(target_returns)
    for r in triggers_returns.values():
        common_dates &= set(r)
    sorted_dates = sorted(common_dates)

    target_dates = [d for _, d in enumerate(sorted_dates)]
    for i, d in enumerate(target_dates):
        if i + spec.horizon_days >= len(target_dates):
            continue
        next_d = target_dates[i + spec.horizon_days]
        all_triggered = all(
            triggers_returns[a].get(d, 0) <= float(spec.trigger_pct)
            for a in triggers_returns
        )
        if all_triggered:
            result.matches.append(
                PatternMatch(
                    pattern=spec,
                    occurred_on=d,
                    next_day_return=target_returns[next_d],
                    triggered=target_returns[next_d] >= float(spec.target_pct),
                )
            )

    if len(result.matches) < min_occurrences:
        result.p_value = 1.0
    else:
        # Binomial simplificado: proporção de matches "triggered"
        successes = sum(1 for m in result.matches if m.triggered)
        result.p_value = round(1 - (successes / len(result.matches)), 4)
    return result
