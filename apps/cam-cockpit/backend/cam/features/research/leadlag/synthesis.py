"""
Síntese regime × gatilho — SPEC v0.5 R-28 (R4). Núcleo puro.

A lente lenta (regime, bar-time) é o PORTEIRO; a rápida (gatilho de fluxo) dá
direção e timing. A composição só é registrada como sobrevivente se SUPERA as
partes isoladas out-of-sample (R-28), com o trial accounting da própria busca
de composição incluído. Sem isso, "dois sinais juntos" é só overfit.

    sinal_operável = 1{regime lento favorável} × gatilho de fluxo rápido
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SynthesisResult:
    mu_gate: float        # expectância só do regime (porteiro)
    mu_trigger: float     # expectância só do gatilho rápido
    mu_combined: float    # expectância da composição
    n_combined: int
    beats_parts: bool     # composição > ambas as partes?
    verdict: str          # SURVIVOR | NO_LIFT | INSUFFICIENT_DATA


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def gated_signal(regime_favorable: list[bool], trigger: list[float]) -> list[float]:
    """
    Composição (R-28): aplica o gatilho rápido SÓ quando o regime lento é
    favorável (porteiro). Fora do regime → 0 (não opera).
    """
    n = min(len(regime_favorable), len(trigger))
    return [trigger[i] if regime_favorable[i] else 0.0 for i in range(n)]


def synthesize(
    regime_favorable: list[bool],
    trigger: list[float],
    target_returns: list[float],
    min_samples: int = 30,
) -> SynthesisResult:
    """
    Mede a composição contra as partes (R-28).

    - `regime_favorable[t]`: lente lenta diz regime favorável em t.
    - `trigger[t]`: sinal direcional da lente rápida em t (sgn usado p/ posição).
    - `target_returns[t]`: retorno do alvo medido APÓS t (anti-look-ahead).

    Retorna expectância de cada parte e da composição; SURVIVOR só se a
    composição supera ambas as partes isoladas.
    """
    n = min(len(regime_favorable), len(trigger), len(target_returns))
    if n < min_samples:
        return SynthesisResult(
            float("nan"), float("nan"), float("nan"), n, False,
            "INSUFFICIENT_DATA",
        )

    def _pos(x: float) -> float:
        return 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)

    # Parte 1 — só regime: posição comprada quando favorável.
    gate_pnl = [
        target_returns[t] if regime_favorable[t] else 0.0 for t in range(n)
    ]
    # Parte 2 — só gatilho: posição sgn(trigger), ignora regime.
    trig_pnl = [_pos(trigger[t]) * target_returns[t] for t in range(n)]
    # Composição — gatilho dentro do regime favorável (porteiro × gatilho).
    comb_pnl = [
        (_pos(trigger[t]) * target_returns[t]) if regime_favorable[t] else 0.0
        for t in range(n)
    ]

    mu_gate = _mean(gate_pnl)
    mu_trig = _mean(trig_pnl)
    mu_comb = _mean(comb_pnl)

    beats = mu_comb > mu_gate and mu_comb > mu_trig and mu_comb > 0
    verdict = "SURVIVOR" if beats else "NO_LIFT"
    return SynthesisResult(mu_gate, mu_trig, mu_comb, n, beats, verdict)
