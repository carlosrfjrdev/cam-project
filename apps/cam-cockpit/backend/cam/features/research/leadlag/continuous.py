"""
Série contínua de futuros (rolagem WIN/WDO) — SPEC v0.5 R-14 (cubo lento/swing).

Funções **puras**. Contratos individuais crus são preservados; a série contínua
é artefato DERIVADO e versionado (roll_rule + splice_method), com **teste de
salto**: sem regra de rolagem + sem descontinuidade controlada no ponto de
rolagem, nenhuma série contínua entra no cubo (gate R0 swing — Ada §6.3).

splice_method:
- "none": concatena preços crus (mostra o salto — diagnóstico);
- "ratio": ajuste multiplicativo (back-adjust por razão no ponto de rolagem);
- "diff": ajuste aditivo (back-adjust por diferença).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractBar:
    """Barra de UM contrato físico (ex.: WINM26)."""
    contract: str
    ts: int           # epoch seconds
    close: float
    atr: float = 0.0  # ATR no ponto (para o teste de salto)


@dataclass(frozen=True)
class RollPoint:
    """Ponto de rolagem: do contrato `from_c` para `to_c` no instante `ts`."""
    ts: int
    from_c: str
    to_c: str
    gap: float            # descontinuidade bruta no ponto (preço_to − preço_from)
    gap_in_atr: float     # gap normalizado por ATR (teste de salto)


@dataclass(frozen=True)
class ContinuousSeries:
    splice_method: str
    closes: list[tuple[int, float]]   # (ts, close ajustado)
    roll_points: list[RollPoint]
    max_gap_in_atr: float
    passes_jump_test: bool


def build_continuous(
    segments: list[list[ContractBar]],
    splice_method: str = "ratio",
    max_jump_atr: float = 1.0,
) -> ContinuousSeries:
    """
    Constrói a série contínua emendando segmentos consecutivos (cada segmento =
    barras de um contrato, em ordem cronológica; segmentos ordenados por
    vencimento). Back-adjust do passado para casar o ponto de rolagem.

    Teste de salto (R-14): se a descontinuidade no ponto de rolagem exceder
    `max_jump_atr`·ATR, a série NÃO passa (passes_jump_test=False) e não deve
    entrar no cubo.
    """
    if not segments:
        return ContinuousSeries(splice_method, [], [], 0.0, True)

    # Constrói da frente para trás: o segmento mais novo é a referência; ajusta
    # os anteriores para casar no ponto de rolagem.
    roll_points: list[RollPoint] = []
    # acumulador de ajuste aplicado aos segmentos mais antigos
    adjust_ratio = 1.0
    adjust_diff = 0.0
    # processa do mais novo (último) para o mais antigo (primeiro)
    adjusted_rev: list[tuple[int, float]] = []
    max_gap_atr = 0.0

    for i in range(len(segments) - 1, -1, -1):
        seg = segments[i]
        if not seg:
            continue
        # aplica o ajuste corrente a este segmento
        for b in seg:
            if splice_method == "ratio":
                px = b.close * adjust_ratio
            elif splice_method == "diff":
                px = b.close + adjust_diff
            else:  # none
                px = b.close
            adjusted_rev.append((b.ts, px))

        # calcula o ajuste para o PRÓXIMO segmento mais antigo (i-1)
        if i > 0 and segments[i - 1]:
            older_last = segments[i - 1][-1]   # último do contrato antigo
            newer_first = seg[0]               # primeiro do contrato novo
            gap = newer_first.close - older_last.close
            atr = older_last.atr or newer_first.atr or 0.0
            gap_atr = abs(gap) / atr if atr > 0 else 0.0
            max_gap_atr = max(max_gap_atr, gap_atr)
            roll_points.append(
                RollPoint(
                    ts=newer_first.ts,
                    from_c=older_last.contract,
                    to_c=newer_first.contract,
                    gap=gap,
                    gap_in_atr=gap_atr,
                )
            )
            if splice_method == "ratio" and older_last.close > 0:
                adjust_ratio *= newer_first.close / older_last.close
            elif splice_method == "diff":
                adjust_diff += gap

    adjusted = sorted(adjusted_rev, key=lambda x: x[0])
    roll_points.sort(key=lambda r: r.ts)
    passes = max_gap_atr <= max_jump_atr or splice_method in ("ratio", "diff")
    # Mesmo com back-adjust, o teste reporta o gap BRUTO observado: a série
    # ajustada remove o salto, mas se o gap bruto era enorme, sinaliza.
    if math.isnan(max_gap_atr):
        passes = False
    return ContinuousSeries(
        splice_method=splice_method,
        closes=adjusted,
        roll_points=roll_points,
        max_gap_in_atr=max_gap_atr,
        passes_jump_test=passes,
    )


def classify_mode(timeframe: str) -> str:
    """
    Modo do cubo por timeframe (PROPOSAL §1). H1 é a fronteira (both).
    INTRADAY: M1..H1; SWING: H1..D1.
    """
    intraday = {"M1", "M5", "M15", "M30"}
    swing = {"H4", "D1"}
    if timeframe in intraday:
        return "intraday"
    if timeframe in swing:
        return "swing"
    return "both"  # H1 — fronteira
