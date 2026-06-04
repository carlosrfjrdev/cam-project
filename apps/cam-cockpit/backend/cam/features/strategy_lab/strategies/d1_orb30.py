"""
D1 — ORB-30 (WIN), single-symbol — lado Python da dupla implementação.

ADR-SL-01: esta é a implementação Python (CAM). O `.mq5` (EA) implementa a
MESMA lógica à mão; a paridade detecta divergência. SEM custo/IR (valores
brutos — R-11). Função pura sobre barras canônicas; o motor (`backtest_engine`)
aplica fill next-bar-open e resolve stop/alvo intrabar.

Lógica (CATALOGO D1):
  1. Opening Range = [high, low] dos primeiros `or_minutes` (default 30) do pregão.
  2. Após o range, entra na QUEBRA: long se preço > OR_high; short se < OR_low.
  3. Stop no extremo oposto do range; alvo = `target_r` × tamanho do range.
  4. Um disparo por direção por dia; flat no fechamento da sessão (sem overnight).

A estratégia emite SINAIS (intenção), não trades — o motor resolve preenchimento.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from cam._shared.research_kernel.bars import Bar


@dataclass(frozen=True)
class D1Params:
    or_minutes: int = 30
    target_r: float = 1.0           # alvo = target_r × range
    session_open: time = time(9, 0)
    session_close: time = time(17, 55)
    entry_until: time = time(17, 0)  # não abre nova posição após este horário


@dataclass(frozen=True)
class Signal:
    """Intenção emitida no fechamento de uma barra. O motor preenche em t+1."""
    bar_index: int
    side: str            # "long" | "short"
    stop_price: float
    target_price: float


def _session_of(bar: Bar) -> str:
    return bar.session_date


def generate_signals(bars: list[Bar], params: D1Params) -> list[Signal]:
    """
    Percorre as barras (de UMA sessão ou várias) e emite sinais de entrada na
    quebra do opening range. Determinístico, sem look-ahead: o sinal nasce no
    fechamento da barra `t` (o motor preenche em `t+1`).
    """
    signals: list[Signal] = []
    cur_session: str | None = None
    or_high: float | None = None
    or_low: float | None = None
    long_armed = True
    short_armed = True

    for i, bar in enumerate(bars):
        tod = bar.ts_open.time()
        session = _session_of(bar)

        # novo pregão → reseta estado
        if session != cur_session:
            cur_session = session
            or_high = None
            or_low = None
            long_armed = True
            short_armed = True

        # 1) construção do opening range (primeiros or_minutes)
        or_end = _add_minutes(params.session_open, params.or_minutes)
        if params.session_open <= tod < or_end:
            or_high = bar.high if or_high is None else max(or_high, bar.high)
            or_low = bar.low if or_low is None else min(or_low, bar.low)
            continue

        if or_high is None or or_low is None:
            continue  # sessão sem range coletado

        # 2) janela de entrada (após o range, antes do corte)
        if tod >= params.entry_until:
            continue

        rng = or_high - or_low
        if rng <= 0:
            continue

        # 3) gatilhos na quebra (decisão no fechamento da barra t)
        if long_armed and bar.close > or_high:
            long_armed = False
            signals.append(
                Signal(
                    bar_index=i,
                    side="long",
                    stop_price=or_low,
                    target_price=or_high + params.target_r * rng,
                )
            )
        elif short_armed and bar.close < or_low:
            short_armed = False
            signals.append(
                Signal(
                    bar_index=i,
                    side="short",
                    stop_price=or_high,
                    target_price=or_low - params.target_r * rng,
                )
            )

    return signals


def _add_minutes(t: time, minutes: int) -> time:
    total = t.hour * 60 + t.minute + minutes
    return time((total // 60) % 24, total % 60)
