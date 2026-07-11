"""
Varredura de grade stop×alvo + expectância por segmento — funções puras.

É a peça que responde "qual stop/alvo é ótimo, e isso muda por regime?". Para
cada par (stop, alvo) da grade, simula o bracket sobre TODOS os trades (via
`simulate_bracket`, pessimista) e agrega a expectância em pontos. Depois segmenta
por regime / hora / lado para revelar onde o edge vive e qual stop sobrevive ao
ruído em cada contexto.

Não reusa `strategy_lab.metrics.GrossMetrics` de propósito: aquele opera sobre
"legs" em R$ de um backtest de estratégia; aqui a unidade é o resultado em pontos
de um bracket simulado sobre trades reais. A agregação é trivial e fica inline.

Zero I/O. Alimentado pelos candles (research_bars) + trades parseados.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from cam._shared.research_kernel.excursion import Candle, simulate_bracket


@dataclass(frozen=True)
class TradeContext:
    """Um trade pronto para simulação: direção, entrada e janela de candles."""

    direction: str            # LONG | SHORT
    entry_price: float
    entry_ts: float           # epoch segundos
    window: Sequence[Candle]  # candles da entrada até o fim da janela/EOD
    regime: str = "INDEFINIDO"
    hour: int = -1
    side: str = ""            # Compra | Venda


@dataclass(frozen=True)
class GridCell:
    """Métricas agregadas de UM par (stop, alvo) sobre um conjunto de trades."""

    stop_pts: float
    target_pts: float
    n: int
    expectancy_pts: float     # média de pontos por trade (o número-chave)
    win_rate: float           # % de trades com result > 0
    profit_factor: float
    avg_win: float
    avg_loss: float
    payoff: float
    target_hits: int
    stop_hits: int


def _aggregate(stop: float, target: float, results: list[float]) -> GridCell:
    n = len(results)
    if n == 0:
        return GridCell(stop, target, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0)
    wins = [r for r in results if r > 0]
    losses = [r for r in results if r < 0]
    gw, gl = sum(wins), abs(sum(losses))
    avg_win = (gw / len(wins)) if wins else 0.0
    avg_loss = (gl / len(losses)) if losses else 0.0
    return GridCell(
        stop_pts=stop,
        target_pts=target,
        n=n,
        expectancy_pts=round(sum(results) / n, 1),
        win_rate=round(len(wins) / n * 100, 1),
        profit_factor=round(gw / gl, 2) if gl else (float("inf") if gw else 0.0),
        avg_win=round(avg_win, 1),
        avg_loss=round(-avg_loss, 1),
        payoff=round(avg_win / avg_loss, 2) if avg_loss else 0.0,
        target_hits=sum(1 for r in results if r >= target),
        stop_hits=sum(1 for r in results if r <= -stop),
    )


def evaluate_grid(
    trades: Sequence[TradeContext],
    stops: Sequence[float],
    targets: Sequence[float],
) -> list[GridCell]:
    """Uma GridCell por combinação (stop, alvo), agregando todos os trades."""
    cells: list[GridCell] = []
    for stop in stops:
        for target in targets:
            results = [
                simulate_bracket(
                    t.entry_price, t.direction, t.window, t.entry_ts, stop, target
                ).result_pts
                for t in trades
            ]
            cells.append(_aggregate(stop, target, results))
    return cells


def best_cell(cells: Sequence[GridCell], min_trades: int = 1) -> GridCell | None:
    """Melhor par por expectância, exigindo amostra mínima (evita overfit em n baixo)."""
    candidates = [c for c in cells if c.n >= min_trades]
    if not candidates:
        return None
    return max(candidates, key=lambda c: c.expectancy_pts)


@dataclass(frozen=True)
class SegmentResult:
    """Grade + melhor par para um segmento (ex.: um regime)."""

    segment: str
    n: int
    best: GridCell | None
    grid: list[GridCell] = field(default_factory=list)


def evaluate_by_segment(
    trades: Sequence[TradeContext],
    stops: Sequence[float],
    targets: Sequence[float],
    key: Callable[[TradeContext], str],
    min_trades: int = 1,
) -> list[SegmentResult]:
    """
    Agrupa trades por `key` (ex.: lambda t: t.regime) e roda a grade em cada grupo.

    Devolve, por segmento, a grade completa + o par ótimo — a tabela
    "regime → (stop, alvo, expectância)" que o Founder pediu.
    """
    groups: dict[str, list[TradeContext]] = {}
    for t in trades:
        groups.setdefault(key(t), []).append(t)

    out: list[SegmentResult] = []
    for seg in sorted(groups):
        grp = groups[seg]
        grid = evaluate_grid(grp, stops, targets)
        out.append(
            SegmentResult(
                segment=seg, n=len(grp),
                best=best_cell(grid, min_trades), grid=grid,
            )
        )
    return out
