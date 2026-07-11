"""
Estrutura de preço + Fibonacci como RÉU — SPEC v0.5 R-26/R-27 (cubo lento).

Funções **puras**. Estrutura mecânica anti-hindsight (swing por ZigZag, pivô
fractal, S/R) definida por regra fixa ANTES do teste. Fibonacci é tratado como
réu: só "fica" se o modelo aninhado B (baseline + fib) supera A (baseline) com
significância, e o coeficiente sobrevive aos controles de redundância (R-27).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Razões de Fibonacci (retração e extensão).
FIB_RETRACE = (0.236, 0.382, 0.5, 0.618, 0.786)
FIB_EXTEND = (1.272, 1.618, 2.618)


# --------------------------------------------------------------------------- #
# Swing mecânico (ZigZag) e pivô fractal — R-26
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SwingPoint:
    index: int
    price: float
    kind: str  # "high" | "low"


def zigzag(prices: list[float], threshold: float) -> list[SwingPoint]:
    """
    Swing por ZigZag (R-26): novo ponto confirmado quando o preço reverte
    ≥ `threshold` (fração) do último extremo. Determinístico, sem hindsight.
    """
    if len(prices) < 2:
        return []
    points: list[SwingPoint] = []
    hi_ext, hi_idx = prices[0], 0   # candidato a topo
    lo_ext, lo_idx = prices[0], 0   # candidato a fundo
    direction = 0  # 0 indefinido, +1 subindo, -1 descendo
    for i in range(1, len(prices)):
        p = prices[i]
        if p > hi_ext:
            hi_ext, hi_idx = p, i
        if p < lo_ext:
            lo_ext, lo_idx = p, i

        up_rev = (p - hi_ext) / hi_ext if hi_ext != 0 else 0.0   # queda desde o topo
        dn_rev = (p - lo_ext) / lo_ext if lo_ext != 0 else 0.0   # alta desde o fundo

        if direction >= 0 and up_rev <= -threshold:
            # caiu ≥ threshold desde o topo → confirma swing high
            points.append(SwingPoint(hi_idx, hi_ext, "high"))
            direction = -1
            lo_ext, lo_idx = p, i  # reinicia candidato a fundo
        elif direction <= 0 and dn_rev >= threshold:
            points.append(SwingPoint(lo_idx, lo_ext, "low"))
            direction = 1
            hi_ext, hi_idx = p, i  # reinicia candidato a topo
    return points


def fractal_pivots(prices: list[float], n: int = 2) -> list[SwingPoint]:
    """Pivô fractal de ordem n (R-26): topo se P(t) > P(t±1..n)."""
    out: list[SwingPoint] = []
    for t in range(n, len(prices) - n):
        window = prices[t - n : t + n + 1]
        if prices[t] == max(window) and prices[t] > min(window):
            out.append(SwingPoint(t, prices[t], "high"))
        elif prices[t] == min(window) and prices[t] < max(window):
            out.append(SwingPoint(t, prices[t], "low"))
    return out


# --------------------------------------------------------------------------- #
# Níveis de Fibonacci + feature de toque (R-27)
# --------------------------------------------------------------------------- #
def fib_levels(p0: float, p1: float) -> dict[float, float]:
    """
    Níveis de retração L_φ = P1 − φ(P1−P0) e extensão E_φ = P1 + (φ−1)(P1−P0),
    para uma perna de swing P0→P1 (R-27).
    """
    span = p1 - p0
    levels = {phi: p1 - phi * span for phi in FIB_RETRACE}
    for phi in FIB_EXTEND:
        levels[phi] = p1 + (phi - 1.0) * span
    return levels


def touch_distance(price: float, level: float, atr: float) -> float:
    """Distância normalizada por ATR: d_φ = |P − L_φ| / ATR (R-27)."""
    if atr <= 0:
        return math.inf
    return abs(price - level) / atr


def is_touch(price: float, level: float, atr: float, eta: float = 0.25) -> bool:
    """Toque se d_φ < η (R-27)."""
    return touch_distance(price, level, atr) < eta


# --------------------------------------------------------------------------- #
# Teste de modelo aninhado A vs B — Fib é réu (R-27)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FibVerdict:
    mu_a: float          # expectância do baseline (sem fib)
    mu_b: float          # expectância do augmentado (com fib)
    delta: float         # mu_b − mu_a (edge incremental do fib)
    n_a: int
    n_b: int
    fib_stays: bool      # fib só fica se delta > 0 com amostra suficiente
    reason: str


def nested_ab_test(
    baseline_outcomes: list[float],
    fib_outcomes: list[float],
    min_samples: int = 30,
) -> FibVerdict:
    """
    Compara A (baseline) vs B (toques de fib). Fib FICA só se μ_B > μ_A com
    amostra suficiente nos dois (R-27). Caso contrário, fib é S/R reetiquetado
    → cai, usa-se o baseline. Δ é o edge incremental.

    `baseline_outcomes`/`fib_outcomes`: retornos assinados pós-evento de cada
    grupo (estrutura genérica vs toque de fib no mesmo ponto).
    """
    na, nb = len(baseline_outcomes), len(fib_outcomes)
    if na < min_samples or nb < min_samples:
        return FibVerdict(
            mu_a=float("nan"), mu_b=float("nan"), delta=float("nan"),
            n_a=na, n_b=nb, fib_stays=False,
            reason="INSUFFICIENT_DATA",
        )
    mu_a = sum(baseline_outcomes) / na
    mu_b = sum(fib_outcomes) / nb
    delta = mu_b - mu_a
    if delta > 0:
        return FibVerdict(mu_a, mu_b, delta, na, nb, True, "FIB_STAYS")
    return FibVerdict(mu_a, mu_b, delta, na, nb, False, "FIB_DROPPED_USE_BASELINE")
