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
    target_r: float = 1.0           # modo RANGE: alvo = target_r × range
    # modo ESTÁTICO (R-15b): exits fixos em pontos do ativo, RELATIVOS à entrada.
    # Ativo quando stop_points > 0 (tem prioridade sobre o range). Componentes:
    #   stop_points    — SL inicial (obrigatório no modo estático).
    #   target_points  — TP fixo OPCIONAL (0 = sem TP; deixa correr no trailing).
    #   trail_points   — STOP MÓVEL OPCIONAL (R-15c): segue o pico a `trail_points`
    #                    de distância; o stop só anda a favor, nunca recua. 0 = off.
    stop_points: float = 0.0
    target_points: float = 0.0
    trail_points: float = 0.0
    session_open: time = time(9, 0)
    session_close: time = time(17, 55)
    entry_until: time = time(17, 0)  # não abre nova posição após este horário

    @property
    def static_exits(self) -> bool:
        return self.stop_points > 0


@dataclass(frozen=True)
class Signal:
    """
    Intenção emitida no fechamento de uma barra. O motor preenche em t+1.

    Modo RANGE: carrega `stop_price`/`target_price` absolutos (conhecidos no
    sinal, pois vêm do opening range). Modo ESTÁTICO: carrega `stop_points`/
    `target_points` (pontos relativos à entrada — o motor resolve no fill, pois
    a entrada só é conhecida em t+1).
    """
    bar_index: int
    side: str            # "long" | "short"
    stop_price: float = 0.0
    target_price: float = 0.0
    stop_points: float = 0.0
    target_points: float = 0.0
    trail_points: float = 0.0


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
            signals.append(_make_signal(i, "long", or_high, or_low, rng, params))
        elif short_armed and bar.close < or_low:
            short_armed = False
            signals.append(_make_signal(i, "short", or_high, or_low, rng, params))

    return signals


def _make_signal(
    i: int, side: str, or_high: float, or_low: float, rng: float, params: D1Params
) -> Signal:
    """Emite o sinal no modo estático (pontos) ou range (preço absoluto)."""
    if params.static_exits:
        # Exits estáticos resolvidos no fill (relativos à entrada — R-15b/R-15c).
        return Signal(
            bar_index=i,
            side=side,
            stop_points=params.stop_points,
            target_points=params.target_points,
            trail_points=params.trail_points,
        )
    # modo range: stop no extremo oposto, alvo = target_r × range (absolutos).
    if side == "long":
        return Signal(
            bar_index=i, side="long",
            stop_price=or_low, target_price=or_high + params.target_r * rng,
        )
    return Signal(
        bar_index=i, side="short",
        stop_price=or_high, target_price=or_low - params.target_r * rng,
    )


def _add_minutes(t: time, minutes: int) -> time:
    total = t.hour * 60 + t.minute + minutes
    return time((total // 60) % 24, total % 60)
