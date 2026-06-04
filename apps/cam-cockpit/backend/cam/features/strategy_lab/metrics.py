"""
Métricas brutas canônicas — rotina ÚNICA (R-17, ADR-SL-02).

A MESMA função consome o ledger do Python e o ledger do EA → elimina divergência
de cálculo na paridade. Tudo BRUTO (sem custo/IR). Zero I/O.
"""
from __future__ import annotations

from dataclasses import dataclass

from cam.features.strategy_lab.domain import LegTrade, PairTrade, aggregate_by_pair


@dataclass(frozen=True)
class GrossMetrics:
    n_trades: int
    wins: int
    losses: int
    win_rate: float
    pnl_bruto_total: float
    avg_win: float
    avg_loss: float          # valor positivo (módulo)
    profit_factor: float     # ganhos / perdas (abs); inf se sem perdas
    payoff: float            # avg_win / avg_loss
    max_drawdown: float      # maior queda pico→vale da equity bruta
    volume_financeiro: float

    def to_dict(self) -> dict:
        return {
            "n_trades": self.n_trades,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": round(self.win_rate, 4),
            "pnl_bruto_total": round(self.pnl_bruto_total, 2),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "profit_factor": (
                None if self.profit_factor == float("inf")
                else round(self.profit_factor, 4)
            ),
            "payoff": (
                None if self.payoff == float("inf") else round(self.payoff, 4)
            ),
            "max_drawdown": round(self.max_drawdown, 2),
            "volume_financeiro": round(self.volume_financeiro, 2),
        }


def equity_curve(pairs: list[PairTrade]) -> list[float]:
    """Curva de equity bruta acumulada (por trade-par, ordem de saída)."""
    ordered = sorted(pairs, key=lambda p: p.ts_exit)
    eq = 0.0
    out: list[float] = []
    for p in ordered:
        eq += p.pnl_bruto
        out.append(eq)
    return out


def _max_drawdown(curve: list[float]) -> float:
    peak = 0.0
    mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v - peak)
    return mdd


def compute_metrics(legs: list[LegTrade]) -> GrossMetrics:
    """Métricas brutas a partir do ledger de pernas (par como unidade)."""
    pairs = aggregate_by_pair(legs)
    n = len(pairs)
    if n == 0:
        return GrossMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    wins = [p.pnl_bruto for p in pairs if p.pnl_bruto > 0]
    losses = [p.pnl_bruto for p in pairs if p.pnl_bruto <= 0]
    sum_win = sum(wins)
    sum_loss_abs = abs(sum(losses))
    avg_win = sum_win / len(wins) if wins else 0.0
    avg_loss = sum_loss_abs / len(losses) if losses else 0.0
    pf = sum_win / sum_loss_abs if sum_loss_abs > 0 else float("inf")
    payoff = avg_win / avg_loss if avg_loss > 0 else float("inf")
    curve = equity_curve(pairs)

    return GrossMetrics(
        n_trades=n,
        wins=len(wins),
        losses=len(losses),
        win_rate=len(wins) / n,
        pnl_bruto_total=sum(p.pnl_bruto for p in pairs),
        avg_win=avg_win,
        avg_loss=avg_loss,
        profit_factor=pf,
        payoff=payoff,
        max_drawdown=_max_drawdown(curve),
        volume_financeiro=sum(p.volume_financeiro for p in pairs),
    )
