"""
Domínio do StrategyLab — value objects puros (ADR-SL-02).

Ledger de trades canônico (schema único Py↔EA), conjuntos de parâmetros, e
agregação par-como-unidade. Sem custo/IR/pnl_liquido (MVP de valores brutos).
Zero I/O — testável isoladamente.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Unit(StrEnum):
    """Unidade da estratégia (ADR-SL-01)."""
    SINGLE = "single"
    PAIR = "pair"
    BASKET = "basket"


class Leg(StrEnum):
    LONG = "long"
    SHORT = "short"


class ParamOrigin(StrEnum):
    MANUAL = "manual"
    SUGGESTED = "suggested"


@dataclass(frozen=True)
class LegTrade:
    """
    Uma perna de um trade. `single` = par de uma perna. A unidade de
    contabilização é o PAR (agrupado por `pair_id`) — par como unidade (R-19).
    Valores BRUTOS: sem custo/IR (R-11).
    """
    pair_id: int
    leg: Leg
    symbol: str
    ts_entry: datetime
    price_entry: float
    ts_exit: datetime
    price_exit: float
    qty: int
    exit_reason: str  # stop | target | time | session | signal
    point_value: float = 1.0  # valor financeiro de 1 ponto/unidade do ativo

    @property
    def pnl_bruto(self) -> float:
        """P&L bruto em moeda: (saída−entrada) × sinal × qtd × valor_do_ponto."""
        direction = 1.0 if self.leg == Leg.LONG else -1.0
        delta = (self.price_exit - self.price_entry) * direction
        return delta * self.qty * self.point_value

    @property
    def volume_financeiro(self) -> float:
        """Volume financeiro bruto operado (entrada + saída), |valor|."""
        return (
            abs(self.price_entry) + abs(self.price_exit)
        ) * self.qty * self.point_value


@dataclass(frozen=True)
class PairTrade:
    """
    Trade como unidade (R-19). Agrega as pernas pelo `pair_id`. Para `single`,
    tem uma perna; para `pair`, duas (long + short).
    """
    pair_id: int
    legs: list[LegTrade] = field(default_factory=list)

    @property
    def pnl_bruto(self) -> float:
        return sum(leg.pnl_bruto for leg in self.legs)

    @property
    def volume_financeiro(self) -> float:
        return sum(leg.volume_financeiro for leg in self.legs)

    @property
    def is_win(self) -> bool:
        return self.pnl_bruto > 0

    @property
    def ts_entry(self) -> datetime:
        return min(leg.ts_entry for leg in self.legs)

    @property
    def ts_exit(self) -> datetime:
        return max(leg.ts_exit for leg in self.legs)


def aggregate_by_pair(legs: list[LegTrade]) -> list[PairTrade]:
    """Agrupa pernas em trades-par por `pair_id`, ordenado por entrada."""
    groups: dict[int, list[LegTrade]] = {}
    for leg in legs:
        groups.setdefault(leg.pair_id, []).append(leg)
    pairs = [PairTrade(pair_id=pid, legs=lg) for pid, lg in groups.items()]
    return sorted(pairs, key=lambda p: p.ts_entry)


@dataclass(frozen=True)
class ParamSet:
    """Conjunto de parâmetros de uma estratégia (R-04/R-08)."""
    strategy_id: str
    params: dict
    origin: ParamOrigin = ParamOrigin.MANUAL
    optimization_id: int | None = None
