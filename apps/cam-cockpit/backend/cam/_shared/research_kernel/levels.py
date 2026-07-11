"""
Detecção de topos/fundos (swing pivots) + clustering de níveis próximos.

Algoritmo (puro, determinístico):
1. PIVÔS fractais: a barra i é topo se `high[i]` é o máximo da janela
   [i-span, i+span]; fundo se `low[i]` é o mínimo. `span` controla a sensibilidade
   (quanto maior, menos pivôs e mais relevantes).
2. CLUSTERING de "variações próximas": os preços dos pivôs são agrupados quando
   ficam dentro de `tol` (fração do preço). Cada cluster vira UM nível horizontal,
   cujo preço é a média dos toques e a força = nº de toques (quantos pivôs caíram
   ali). Níveis tocados mais vezes = suporte/resistência mais relevante.

Saída: níveis ordenados por força (desc), com tipo (resistance/support/both),
preço, nº de toques e janela temporal — prontos para virar linha horizontal.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cam._shared.research_kernel.bars import Bar


@dataclass(frozen=True)
class Pivot:
    index: int
    price: float
    kind: str  # "high" | "low"
    ts: str    # ISO


@dataclass(frozen=True)
class Level:
    price: float
    kind: str         # "resistance" | "support" | "both"
    touches: int
    strength: float   # touches normalizado p/ ordenação (== touches por ora)
    first_ts: str
    last_ts: str


def detect_pivots(bars: Sequence[Bar], span: int = 3) -> list[Pivot]:
    """Pivôs fractais com janela simétrica `span`."""
    pivots: list[Pivot] = []
    n = len(bars)
    if n < 2 * span + 1:
        return pivots
    for i in range(span, n - span):
        window = bars[i - span : i + span + 1]
        hi = bars[i].high
        lo = bars[i].low
        is_high = hi >= max(b.high for b in window) and hi > bars[i - 1].high
        is_low = lo <= min(b.low for b in window) and lo < bars[i - 1].low
        if is_high:
            pivots.append(Pivot(i, hi, "high", bars[i].ts_open.isoformat()))
        if is_low:
            pivots.append(Pivot(i, lo, "low", bars[i].ts_open.isoformat()))
    return pivots


def cluster_levels(
    pivots: Sequence[Pivot], tol: float = 0.0015, min_touches: int = 1
) -> list[Level]:
    """
    Agrupa pivôs com preços próximos (dentro de `tol` relativo) em níveis.
    `tol`: fração do preço (0.0015 = 0,15%). `min_touches`: descarta níveis fracos.
    """
    if not pivots:
        return []
    ordered = sorted(pivots, key=lambda p: p.price)
    clusters: list[list[Pivot]] = [[ordered[0]]]
    for p in ordered[1:]:
        ref = clusters[-1][0].price
        if abs(p.price - ref) <= tol * ref:
            clusters[-1].append(p)
        else:
            clusters.append([p])

    levels: list[Level] = []
    for group in clusters:
        if len(group) < min_touches:
            continue
        price = sum(g.price for g in group) / len(group)
        highs = sum(1 for g in group if g.kind == "high")
        lows = len(group) - highs
        if highs and not lows:
            kind = "resistance"
        elif lows and not highs:
            kind = "support"
        else:
            kind = "both"
        ts_sorted = sorted(group, key=lambda g: g.ts)
        levels.append(
            Level(
                price=round(price, 2),
                kind=kind,
                touches=len(group),
                strength=float(len(group)),
                first_ts=ts_sorted[0].ts,
                last_ts=ts_sorted[-1].ts,
            )
        )
    levels.sort(key=lambda lv: (lv.strength, lv.touches), reverse=True)
    return levels


def detect_levels(
    bars: Sequence[Bar],
    span: int = 3,
    tol: float = 0.0015,
    min_touches: int = 1,
    top_n: int | None = None,
) -> list[Level]:
    """Pipeline completo: pivôs → clustering → níveis (opcionalmente top N)."""
    levels = cluster_levels(detect_pivots(bars, span), tol=tol, min_touches=min_touches)
    return levels[:top_n] if top_n else levels
