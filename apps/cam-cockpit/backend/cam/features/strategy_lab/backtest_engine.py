"""
Motor de backtest MVP-bruto, single-symbol — StrategyLab (ADR-SL-02, R-11/R-12).

NOVO motor, NÃO importa `_shared.risk` nem provisiona IR (modo bruto desacoplado).
Aplica os sinais de uma estratégia com as regras canônicas de paridade (subset
C1–C6, sem C7/C8):
  - fill na ABERTURA da barra seguinte ao sinal (next-bar-open, C4);
  - stop/alvo resolvidos intrabar pelo PIOR caso (se a barra toca os dois,
    assume stop primeiro, C5);
  - gap honesto: se o open ultrapassa o nível, executa no open real (C6);
  - flat compulsório no fechamento da sessão (sem overnight).

Resultado: lista de `LegTrade` (ledger bruto). Determinístico.
"""
from __future__ import annotations

from cam._shared.research_kernel.bars import Bar
from cam.features.strategy_lab.domain import Leg, LegTrade
from cam.features.strategy_lab.strategies.d1_orb30 import D1Params, Signal


def run_d1_backtest(
    bars: list[Bar],
    signals: list[Signal],
    params: D1Params,
    point_value: float = 0.20,
    qty: int = 1,
) -> list[LegTrade]:
    """
    Executa os sinais de D1 sobre as barras. Uma posição por vez (single).
    `point_value` = valor financeiro de 1 ponto do ativo (WIN: 0,20 por ponto).
    """
    trades: list[LegTrade] = []
    pair_id = 0
    sig_by_bar = {s.bar_index: s for s in signals}

    open_pos: _Position | None = None

    for i, bar in enumerate(bars):
        # 1) gerir posição aberta — saídas ANTES de novas entradas (C3)
        if open_pos is not None:
            exit_info = _resolve_exit(open_pos, bar, params)
            if exit_info is not None:
                price_exit, reason = exit_info
                trades.append(
                    LegTrade(
                        pair_id=open_pos.pair_id,
                        leg=open_pos.leg,
                        symbol=bar.symbol,
                        ts_entry=open_pos.ts_entry,
                        price_entry=open_pos.price_entry,
                        ts_exit=bar.ts_open,
                        price_exit=price_exit,
                        qty=qty,
                        exit_reason=reason,
                        point_value=point_value,
                    )
                )
                open_pos = None

        # 2) entrada: sinal nasceu no fechamento de t-1 → preenche no open de t (C4)
        if open_pos is None:
            sig = sig_by_bar.get(i - 1)
            if sig is not None:
                leg = Leg.LONG if sig.side == "long" else Leg.SHORT
                entry = bar.open  # fill next-bar-open
                stop, target, has_target, trail = _resolve_levels(sig, leg, entry)
                open_pos = _Position(
                    pair_id=pair_id,
                    leg=leg,
                    ts_entry=bar.ts_open,
                    price_entry=entry,
                    stop_price=stop,
                    target_price=target,
                    has_target=has_target,
                    trail_points=trail,
                    max_favor=entry,
                )
                pair_id += 1

    # 3) flat no fim da série, se ainda aberta (fecha no último close)
    if open_pos is not None and bars:
        last = bars[-1]
        trades.append(
            LegTrade(
                pair_id=open_pos.pair_id,
                leg=open_pos.leg,
                symbol=last.symbol,
                ts_entry=open_pos.ts_entry,
                price_entry=open_pos.price_entry,
                ts_exit=last.ts_close,
                price_exit=last.close,
                qty=qty,
                exit_reason="session",
                point_value=point_value,
            )
        )

    return trades


def _resolve_levels(
    sig: Signal, leg: Leg, entry: float
) -> tuple[float, float, bool, float]:
    """
    Resolve (stop, alvo, has_target, trail) ABSOLUTOS no momento do fill,
    combinando livremente componentes RELATIVOS (em pontos da entrada) e
    ABSOLUTOS (preço do sinal) — espelha os EAs, que misturam os dois:

      - STOP:  stop_points>0 ⇒ relativo à entrada; senão usa stop_price (absoluto:
               range do ORB ou banda sigma do VWAP).
      - ALVO:  target_points>0 ⇒ relativo; senão target_price>0 (absoluto, ex.: VWAP);
               nenhum dos dois ⇒ sem TP (deixa o trailing/sessão decidir).
      - TRAIL: trail_points (stop móvel; 0 = off).

    Ex.: D2 com stop inicial=0 (sigma), alvo fixo=300 e trail=900 → stop=banda
    sigma absoluta + TP relativo 300 + stop móvel 900.
    """
    is_long = leg == Leg.LONG
    sign = 1.0 if is_long else -1.0

    if sig.stop_points > 0:
        stop = entry - sign * sig.stop_points
    else:
        stop = sig.stop_price

    if sig.target_points > 0:
        target = entry + sign * sig.target_points
        has_target = True
    elif sig.target_price > 0:
        target = sig.target_price
        has_target = True
    else:
        target = 0.0
        has_target = False

    return (stop, target, has_target, sig.trail_points)


class _Position:
    def __init__(
        self, pair_id, leg, ts_entry, price_entry, stop_price, target_price,
        has_target=True, trail_points=0.0, max_favor=0.0,
    ):
        self.pair_id = pair_id
        self.leg = leg
        self.ts_entry = ts_entry
        self.price_entry = price_entry
        self.stop_price = stop_price
        self.target_price = target_price
        self.has_target = has_target
        self.trail_points = trail_points
        self.max_favor = max_favor


def _resolve_exit(
    pos: _Position, bar: Bar, params: D1Params
) -> tuple[float, str] | None:
    """
    Resolve a saída de `pos` dentro de `bar`. Pior caso intrabar (C5): se a barra
    toca stop e alvo, stop primeiro. Gap honesto (C6): se o open já passou do
    nível, sai no open real. TP opcional (`has_target`). Flat na sessão (C11).

    Stop móvel (R-15c): checa a saída com o stop VIGENTE (pico das barras
    ANTERIORES — pior caso); só DEPOIS ratcheta o stop com o extremo desta barra,
    valendo para as próximas. O stop nunca recua.
    """
    is_long = pos.leg == Leg.LONG
    stop, target = pos.stop_price, pos.target_price

    # gap honesto no open
    if is_long:
        if bar.open <= stop:
            return (bar.open, "stop")
        if pos.has_target and bar.open >= target:
            return (bar.open, "target")
    else:
        if bar.open >= stop:
            return (bar.open, "stop")
        if pos.has_target and bar.open <= target:
            return (bar.open, "target")

    # intrabar — pior caso: stop antes do alvo
    if is_long:
        if bar.low <= stop:
            return (stop, "stop")
        if pos.has_target and bar.high >= target:
            return (target, "target")
    else:
        if bar.high >= stop:
            return (stop, "stop")
        if pos.has_target and bar.low <= target:
            return (target, "target")

    # stop móvel: ratcheta o stop com o extremo desta barra (vale p/ as próximas)
    if pos.trail_points > 0:
        if is_long:
            pos.max_favor = max(pos.max_favor, bar.high)
            pos.stop_price = max(pos.stop_price, pos.max_favor - pos.trail_points)
        else:
            pos.max_favor = min(pos.max_favor, bar.low)
            pos.stop_price = min(pos.stop_price, pos.max_favor + pos.trail_points)

    # flat compulsório no fechamento da sessão (sem overnight)
    if _is_session_close(bar, params):
        return (bar.close, "session")

    return None


def _is_session_close(bar: Bar, params: D1Params) -> bool:
    return bar.ts_open.time() >= params.session_close
