"""
Otimizador de parâmetros on-demand — StrategyLab (R-05/R-06/R-07/R-08).

SUGERE, não aplica (R-08). Só roda quando acionado (R-05). Varre o espaço de
parâmetros (grid + random) rodando o backtest, e passa cada candidato pelo
GUARD-RAIL anti-overfit do `_shared/research_kernel/validation` (DSR penalizado
pelo nº de tentativas, no-cliff) — nunca reporta "o pico" sem contexto.

Pure-ish: recebe um `evaluate(params) -> (score, n_trades)` injetado (o caller
liga ao motor de backtest). Determinístico com seed.
"""
from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any

from cam._shared.research_kernel import validation

# evaluate(params) -> (score_sharpe_like, n_trades)
EvalFn = Callable[[dict[str, Any]], tuple[float, int]]


@dataclass(frozen=True)
class OptimResult:
    best_params: dict[str, Any]
    best_score: float
    n_trials: int
    deflated_sharpe: float | None   # DSR penalizado pelo nº de tentativas
    no_cliff: bool                  # robustez: vizinhança do ótimo não desaba
    min_samples_ok: bool            # dados suficientes p/ sugerir
    verdict: str                    # SUGGEST | INSUFFICIENT_DATA


def _grid(space: dict[str, Sequence[Any]]) -> list[dict[str, Any]]:
    keys = list(space.keys())
    return [dict(zip(keys, combo, strict=True)) for combo in product(*space.values())]


def _random_samples(
    space: dict[str, Sequence[Any]], n: int, seed: int
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        out.append({k: rng.choice(list(v)) for k, v in space.items()})
    return out


def optimize(
    space: dict[str, Sequence[Any]],
    evaluate: EvalFn,
    method: str = "grid",
    random_n: int = 50,
    seed: int = 42,
    min_trades: int = 20,
) -> OptimResult:
    """
    Roda a otimização e SUGERE o melhor conjunto com selo de robustez.
    `space`: dict param→lista de valores. `evaluate`: roda o backtest e devolve
    (score, n_trades). `method`: "grid" | "random".
    """
    if method == "random":
        candidates = _random_samples(space, random_n, seed)
    else:
        candidates = _grid(space)

    scored: list[tuple[dict[str, Any], float, int]] = []
    for params in candidates:
        score, n_trades = evaluate(params)
        scored.append((params, score, n_trades))

    n_trials = len(scored)
    # filtra candidatos com amostra mínima
    valid = [s for s in scored if s[2] >= min_trades]
    if not valid:
        return OptimResult(
            best_params={}, best_score=float("nan"), n_trials=n_trials,
            deflated_sharpe=None, no_cliff=False, min_samples_ok=False,
            verdict="INSUFFICIENT_DATA",
        )

    best = max(valid, key=lambda s: s[1])
    best_params, best_score, best_n = best

    # DSR penalizado pelo nº de tentativas (anti-data-snooping, R-07)
    dsr = validation.deflated_sharpe_ratio(
        observed_sr=best_score,
        n_obs=best_n,
        skew=0.0,
        kurtosis=3.0,
        n_trials=n_trials,
    )

    # no-cliff: a vizinhança do ótimo (top-k scores) não é um pico isolado
    sorted_scores = sorted((s[1] for s in valid), reverse=True)
    no_cliff = _is_no_cliff(sorted_scores)

    return OptimResult(
        best_params=best_params,
        best_score=best_score,
        n_trials=n_trials,
        deflated_sharpe=None if dsr != dsr else dsr,  # NaN→None
        no_cliff=no_cliff,
        min_samples_ok=True,
        verdict="SUGGEST",
    )


def _is_no_cliff(sorted_scores: list[float], top_k: int = 5) -> bool:
    """
    Robustez: se o melhor score não é muito superior à média dos próximos,
    a superfície é "chata" (bom). Se o melhor descola muito, é um pico (cliff).
    """
    if len(sorted_scores) < 2:
        return False
    best = sorted_scores[0]
    neighbors = sorted_scores[1 : top_k + 1]
    if not neighbors:
        return False
    avg_neighbors = sum(neighbors) / len(neighbors)
    if best <= 0:
        return False
    # pico se o melhor é >2× a média dos vizinhos
    return best <= 2.0 * max(avg_neighbors, 1e-9)
