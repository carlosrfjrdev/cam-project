"""
MAE/MFE e simulação de bracket stop×alvo — funções puras reutilizáveis.

Extraído de `trade_analyzer.enrichment._simulate`, que acoplava o cálculo de
excursão a um setup fixo 1:3 (stop 100 / alvo 300). Aqui:

- `excursion(...)` calcula MAE/MFE **independente** de qualquer stop/alvo — é o
  raio-X de "até onde o preço foi contra/a favor" a partir da entrada.
- `simulate_bracket(...)` simula UM par (stop, alvo) varrendo candle a candle,
  pessimista (se alvo e stop caem no mesmo candle, assume STOP primeiro). É a
  peça unitária da **varredura de grade** (B3) que descobre o stop/alvo ótimos.

Por que separar: a mesma série de candles alimenta (a) o diagnóstico MAE/MFE e
(b) a otimização de bracket por regime. Mantê-las puras (zero I/O) torna tudo
testável com candles sintéticos, sem bridge nem banco.

Contrato de candle: Mapping com chaves `ts` (epoch segundos, float), `h`, `l`,
`c` (floats). `o` é opcional. WIN: 1 ponto = 1 unidade de preço.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

Candle = Mapping[str, float]


@dataclass(frozen=True)
class Excursion:
    """Excursão de um trade, em pontos, relativa ao preço de entrada."""

    mae_pts: float           # máxima excursão ADVERSA (>= 0)
    mfe_pts: float           # máxima excursão FAVORÁVEL (>= 0)
    time_to_mae_min: float | None  # minutos da entrada até o pior ponto
    time_to_mfe_min: float | None  # minutos da entrada até o melhor ponto
    bars: int                # candles na janela analisada


@dataclass(frozen=True)
class BracketOutcome:
    """Desfecho de um par (stop, alvo) fixo simulado sobre a janela."""

    exit_reason: str         # "target" | "stop" | "none"
    result_pts: float        # +alvo / -stop / mark-to-end (se "none")
    minutes: float | None    # minutos até o desfecho (None se "none")


def select_window(
    candles: Sequence[Candle], start_ts: float, end_ts: float
) -> list[Candle]:
    """Candles com `start_ts <= ts <= end_ts`, preservando a ordem de entrada."""
    return [c for c in candles if start_ts <= c["ts"] <= end_ts]


def _favor_adverse(direction: str, entry: float, c: Candle) -> tuple[float, float]:
    """(favorável, adverso) em pontos para um candle, conforme a direção."""
    is_long = direction == "LONG"
    if is_long:
        return c["h"] - entry, entry - c["l"]
    return entry - c["l"], c["h"] - entry


def excursion(
    entry_price: float,
    direction: str,
    window: Sequence[Candle],
    entry_ts: float,
) -> Excursion:
    """
    MAE/MFE em pontos sobre `window` (já recortada à janela pós-entrada).

    Não conhece stop nem alvo. `direction` ∈ {"LONG","SHORT"}. Tempos são os
    minutos da entrada até o candle que cravou o extremo (primeiro a atingir).
    """
    if not entry_price or not window:
        return Excursion(0.0, 0.0, None, None, 0)

    mfe = mae = 0.0
    t_mfe = t_mae = None
    for c in window:
        favor, adverse = _favor_adverse(direction, entry_price, c)
        if favor > mfe:
            mfe = favor
            t_mfe = round((c["ts"] - entry_ts) / 60.0, 1)
        if adverse > mae:
            mae = adverse
            t_mae = round((c["ts"] - entry_ts) / 60.0, 1)
    return Excursion(
        mae_pts=round(max(0.0, mae), 1),
        mfe_pts=round(max(0.0, mfe), 1),
        time_to_mae_min=t_mae,
        time_to_mfe_min=t_mfe,
        bars=len(window),
    )


def simulate_bracket(
    entry_price: float,
    direction: str,
    window: Sequence[Candle],
    entry_ts: float,
    stop_pts: float,
    target_pts: float,
) -> BracketOutcome:
    """
    Simula um bracket fixo (stop_pts/target_pts) varrendo candle a candle.

    Pessimista: se alvo e stop são tocados no MESMO candle, assume STOP (o pior
    caso — não dá pra saber a ordem intrabar sem ticks). Se nada é tocado até o
    fim da janela, marca a mercado no último close ("none").
    """
    is_long = direction == "LONG"
    if is_long:
        target_px, stop_px = entry_price + target_pts, entry_price - stop_pts
    else:
        target_px, stop_px = entry_price - target_pts, entry_price + stop_pts

    for c in window:
        hit_target = c["h"] >= target_px if is_long else c["l"] <= target_px
        hit_stop = c["l"] <= stop_px if is_long else c["h"] >= stop_px
        if hit_stop:  # pessimista: stop vence empate intrabar
            return BracketOutcome(
                "stop", -stop_pts, round((c["ts"] - entry_ts) / 60.0, 1)
            )
        if hit_target:
            return BracketOutcome(
                "target", target_pts, round((c["ts"] - entry_ts) / 60.0, 1)
            )

    if not window:
        return BracketOutcome("none", 0.0, None)
    last_close = window[-1]["c"]
    captured = (last_close - entry_price) if is_long else (entry_price - last_close)
    return BracketOutcome("none", round(captured, 1), None)
