"""
D2 — VWAP Mean-Reversion fade (WDO), single-symbol — lado Python.

Ficha D2 (catálogo): WDO sem choque macro é mean-reverting intradiário. Faz FADE
da extensão: quando o preço estica ±k_entry·σ do VWAP da sessão, opera CONTRA
(short na esticada pra cima, long na esticada pra baixo); alvo no VWAP; stop além
de k_stop·σ; sem runner (mean-reversion, não tendência). Múltiplos trades/dia.

VWAP e σ são CUMULATIVOS na sessão (resetam a cada pregão), ponderados por volume.
Os níveis de alvo/stop são congelados no fill (absolutos) — espelháveis no EA e
amigáveis à paridade. SEM custo/IR (MVP bruto). Função pura sobre barras canônicas;
reusa o motor single-symbol (run_d1_backtest) via Signal com preços absolutos.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import time

from cam._shared.research_kernel.bars import Bar
from cam.features.strategy_lab.strategies.d1_orb30 import Signal


@dataclass(frozen=True)
class D2Params:
    k_entry: float = 2.0            # esticada de entrada (em σ do VWAP)
    k_stop: float = 3.0             # stop além de k_stop·σ (modo sigma)
    warmup_bars: int = 30           # nº mín. de barras na sessão p/ σ confiável
    # SAÍDA em PONTOS (estilo ORB30, espelha o EA cam_d2_vwap_exec). 0 = usa o
    # modo sigma/VWAP no componente correspondente. Podem-se combinar livremente:
    #   stop_points    — SL estático em pontos (0 = stop na banda VWAP±k_stop·σ).
    #   target_points  — TP fixo em pontos (0 = alvo no próprio VWAP).
    #   trail_points   — stop móvel em pontos atrás do pico (0 = desligado).
    stop_points: float = 0.0
    target_points: float = 0.0
    trail_points: float = 0.0
    session_open: time = time(9, 0)
    session_close: time = time(17, 55)
    entry_until: time = time(17, 0)


def _typical(bar: Bar) -> float:
    return (bar.high + bar.low + bar.close) / 3.0


def generate_signals(bars: list[Bar], params: D2Params) -> list[Signal]:
    """
    Emite sinais de FADE na tocada de ±k_entry·σ do VWAP cumulativo da sessão.
    Um sinal por excursão (arma ao voltar pra dentro da banda; dispara ao cruzar
    pra fora) — evita reentrada imediata na mesma esticada. Alvo = VWAP; stop =
    VWAP ± k_stop·σ (congelados no instante do sinal).
    """
    signals: list[Signal] = []
    cur_session: str | None = None
    sum_pv = sum_v = sum_pv2 = 0.0
    n_in_session = 0
    armed_long = armed_short = True

    for i, bar in enumerate(bars):
        tod = bar.ts_open.time()

        if bar.session_date != cur_session:
            cur_session = bar.session_date
            sum_pv = sum_v = sum_pv2 = 0.0
            n_in_session = 0
            armed_long = armed_short = True

        # acumula VWAP/σ da sessão (ponderado por volume; fallback volume=1)
        tp = _typical(bar)
        vol = float(bar.volume) if bar.volume else 1.0
        sum_pv += tp * vol
        sum_v += vol
        sum_pv2 += tp * tp * vol
        n_in_session += 1

        if not (params.session_open <= tod < params.entry_until):
            continue
        if n_in_session < params.warmup_bars or sum_v <= 0:
            continue

        vwap = sum_pv / sum_v
        var = max(0.0, sum_pv2 / sum_v - vwap * vwap)
        sigma = math.sqrt(var)
        if sigma <= 0:
            continue

        upper_e = vwap + params.k_entry * sigma
        lower_e = vwap - params.k_entry * sigma

        # re-arma quando o preço volta pra dentro da banda de entrada
        if lower_e <= bar.close <= upper_e:
            armed_long = armed_short = True
            continue

        # fade: esticou pra cima → short; esticou pra baixo → long.
        # Saída: banda sigma (stop_price=VWAP±k_stop·σ, alvo=VWAP) como base;
        # os componentes em PONTOS (stop/target/trail), se > 0, substituem no
        # motor (_resolve_levels). Espelha o EA cam_d2_vwap_exec.
        if armed_short and bar.close > upper_e:
            armed_short = False
            signals.append(
                Signal(
                    bar_index=i, side="short",
                    stop_price=vwap + params.k_stop * sigma,
                    target_price=vwap,
                    stop_points=params.stop_points,
                    target_points=params.target_points,
                    trail_points=params.trail_points,
                )
            )
        elif armed_long and bar.close < lower_e:
            armed_long = False
            signals.append(
                Signal(
                    bar_index=i, side="long",
                    stop_price=vwap - params.k_stop * sigma,
                    target_price=vwap,
                    stop_points=params.stop_points,
                    target_points=params.target_points,
                    trail_points=params.trail_points,
                )
            )

    return signals
