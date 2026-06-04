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
                open_pos = _Position(
                    pair_id=pair_id,
                    leg=leg,
                    ts_entry=bar.ts_open,
                    price_entry=bar.open,  # fill next-bar-open
                    stop_price=sig.stop_price,
                    target_price=sig.target_price,
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


class _Position:
    def __init__(self, pair_id, leg, ts_entry, price_entry, stop_price, target_price):
        self.pair_id = pair_id
        self.leg = leg
        self.ts_entry = ts_entry
        self.price_entry = price_entry
        self.stop_price = stop_price
        self.target_price = target_price


def _resolve_exit(
    pos: _Position, bar: Bar, params: D1Params
) -> tuple[float, str] | None:
    """
    Resolve a saída de `pos` dentro de `bar`. Pior caso intrabar (C5): se a barra
    toca stop e alvo, stop primeiro. Gap honesto (C6): se o open já passou do
    nível, sai no open real. Flat na sessão (C11) se for a última barra do dia.
    """
    is_long = pos.leg == Leg.LONG
    stop, target = pos.stop_price, pos.target_price

    # gap honesto no open
    if is_long:
        if bar.open <= stop:
            return (bar.open, "stop")
        if bar.open >= target:
            return (bar.open, "target")
    else:
        if bar.open >= stop:
            return (bar.open, "stop")
        if bar.open <= target:
            return (bar.open, "target")

    # intrabar — pior caso: stop antes do alvo
    if is_long:
        if bar.low <= stop:
            return (stop, "stop")
        if bar.high >= target:
            return (target, "target")
    else:
        if bar.high >= stop:
            return (stop, "stop")
        if bar.low <= target:
            return (target, "target")

    # flat compulsório no fechamento da sessão (sem overnight)
    if _is_session_close(bar, params):
        return (bar.close, "session")

    return None


def _is_session_close(bar: Bar, params: D1Params) -> bool:
    return bar.ts_open.time() >= params.session_close
