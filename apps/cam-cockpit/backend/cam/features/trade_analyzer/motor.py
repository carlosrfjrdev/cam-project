"""
Motor estatístico do trade_analyzer: trades reais + candles → bracket ótimo por regime.

Junta as peças puras do research_kernel (excursion, regime_intraday,
bracket_optimizer) num pipeline que responde às perguntas do Founder:
  1. Qual (stop, alvo) tem maior expectância — global e POR REGIME?
  2. "80 pts é pullback certo num regime?" → distribuição de MAE dos VENCEDORES
     por regime: o stop precisa ficar acima da MAE típica do vencedor, senão
     mata trades que iam dar certo.

Vive na feature (conhece `Trade`); só importa para baixo (research_kernel),
nunca outra feature (ADR-013). Recebe os candles já carregados — a busca via
bridge/banco fica no script/serviço que chama isto. Testável com candles
sintéticos.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from cam._shared.research_kernel.bracket_optimizer import (
    TradeContext,
    best_cell,
    evaluate_by_segment,
    evaluate_grid,
)
from cam._shared.research_kernel.excursion import (
    Candle,
    excursion,
    select_window,
)
from cam._shared.research_kernel.regime_intraday import (
    DEFAULT_LOOKBACK,
    DEFAULT_TREND_THRESHOLD,
    label_trade,
)
from cam.features.trade_analyzer.metrics import Trade

BR_TZ = ZoneInfo("America/Sao_Paulo")
DEFAULT_STOPS = [40.0, 60.0, 80.0, 100.0, 120.0, 150.0]
DEFAULT_TARGETS = [80.0, 120.0, 160.0, 200.0, 300.0, 400.0]
DEFAULT_HORIZON_MIN = 120


def _entry_ts(trade: Trade) -> float:
    return trade.abertura.replace(tzinfo=BR_TZ).timestamp()


def _window_end(entry_ts: float) -> float:
    """Entrada + horizonte, capado no fim do dia (BR)."""
    dt = datetime.fromtimestamp(entry_ts, BR_TZ)
    eod = dt.replace(hour=23, minute=59, second=59).timestamp()
    return min(entry_ts + DEFAULT_HORIZON_MIN * 60, eod)


def build_contexts(
    trades: Sequence[Trade],
    candles: Sequence[Candle],
    lookback: int = DEFAULT_LOOKBACK,
    trend_threshold: float = DEFAULT_TREND_THRESHOLD,
) -> list[TradeContext]:
    """Constrói um TradeContext por trade (com janela e regime na entrada)."""
    ctxs: list[TradeContext] = []
    for t in trades:
        ets = _entry_ts(t)
        window = select_window(candles, ets, _window_end(ets))
        regime = label_trade(candles, ets, lookback, trend_threshold)
        ctxs.append(
            TradeContext(
                direction=t.direction or ("LONG" if t.lado == "C" else "SHORT"),
                entry_price=t.entry_price,
                entry_ts=ets,
                window=window,
                regime=regime,
                hour=t.abertura.hour,
                side="Compra" if t.lado == "C" else "Venda",
            )
        )
    return ctxs


def _percentile(values: list[float], p: float) -> float:
    """Percentil simples (interpolação linear). `p` em [0,100]."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return round(s[0], 1)
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    frac = k - lo
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * frac, 1)


def winners_mae_by_regime(ctxs: Sequence[TradeContext]) -> dict[str, dict]:
    """
    Distribuição de MAE dos trades VENCEDORES por regime.

    "Vencedor" = MFE > MAE e MFE > 0 (o preço chegou a oferecer lucro). O stop
    ideal por regime fica ACIMA do p75/p90 da MAE desses — abaixo disso, você é
    estopado em trades que iam dar certo (o "pullback certo" que o Founder citou).
    """
    by: dict[str, list[float]] = {}
    for c in ctxs:
        if not c.window:
            continue
        ex = excursion(c.entry_price, c.direction, c.window, c.entry_ts)
        if ex.mfe_pts > ex.mae_pts and ex.mfe_pts > 0:
            by.setdefault(c.regime, []).append(ex.mae_pts)
    out: dict[str, dict] = {}
    for regime, maes in sorted(by.items()):
        out[regime] = {
            "n_vencedores": len(maes),
            "mae_mediana": _percentile(maes, 50),
            "mae_p75": _percentile(maes, 75),
            "mae_p90": _percentile(maes, 90),
            "stop_sugerido_min": _percentile(maes, 75),
        }
    return out


def _cell_dict(cell) -> dict | None:
    if cell is None:
        return None
    return {
        "stop_pts": cell.stop_pts,
        "target_pts": cell.target_pts,
        "rr": round(cell.target_pts / cell.stop_pts, 2) if cell.stop_pts else None,
        "n": cell.n,
        "expectancy_pts": cell.expectancy_pts,
        "win_rate": cell.win_rate,
        "profit_factor": cell.profit_factor,
        "payoff": cell.payoff,
    }


def run_motor(
    trades: Sequence[Trade],
    candles: Sequence[Candle],
    stops: Sequence[float] = tuple(DEFAULT_STOPS),
    targets: Sequence[float] = tuple(DEFAULT_TARGETS),
    lookback: int = DEFAULT_LOOKBACK,
    trend_threshold: float = DEFAULT_TREND_THRESHOLD,
    min_trades: int = 5,
) -> dict:
    """
    Pipeline completo → dict serializável: cobertura, melhor (stop,alvo) global,
    tabela por regime/hora/lado, e MAE dos vencedores por regime.
    """
    ctxs_all = build_contexts(trades, candles, lookback, trend_threshold)
    ctxs = [c for c in ctxs_all if c.window]

    overall = evaluate_grid(ctxs, stops, targets)
    by_regime = evaluate_by_segment(
        ctxs, stops, targets, key=lambda c: c.regime, min_trades=min_trades
    )
    by_hour = evaluate_by_segment(
        ctxs, stops, targets, key=lambda c: f"{c.hour:02d}h", min_trades=min_trades
    )
    by_side = evaluate_by_segment(
        ctxs, stops, targets, key=lambda c: c.side, min_trades=min_trades
    )

    def _seg(segs):
        return [
            {"segmento": s.segment, "n": s.n, "melhor": _cell_dict(s.best)}
            for s in segs
        ]

    return {
        "cobertura": {
            "total_trades": len(ctxs_all),
            "com_candles": len(ctxs),
            "sem_candles": len(ctxs_all) - len(ctxs),
        },
        "grade": {"stops": list(stops), "targets": list(targets)},
        "melhor_global": _cell_dict(best_cell(overall, min_trades)),
        "por_regime": _seg(by_regime),
        "por_hora": _seg(by_hour),
        "por_lado": _seg(by_side),
        "mae_vencedores_por_regime": winners_mae_by_regime(ctxs),
    }
