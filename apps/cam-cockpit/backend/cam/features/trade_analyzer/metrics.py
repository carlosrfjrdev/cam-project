"""
Parser + métricas determinísticas do report de operações.

Suporta o layout Profit/Genial (semicolon, latin-1):
  Ativo;Abertura;Fechamento;Tempo Operação;Qtd Compra;Qtd Venda;Lado;
  Preço Compra;Preço Venda;...;Res. Operação;...

As métricas são calculadas em código (não pela IA) — números confiáveis que
alimentam o prompt. A IA recebe esse resumo e produz a narrativa.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Trade:
    asset: str
    abertura: datetime
    fechamento: datetime
    lado: str  # C / V
    qty: int
    result: float
    duration_s: float


@dataclass
class TradeMetrics:
    total_trades: int = 0
    gross_result: float = 0.0
    wins: int = 0
    losses: int = 0
    zeros: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    payoff: float = 0.0
    profit_factor: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    by_day: list[dict] = field(default_factory=list)
    by_hour: list[dict] = field(default_factory=list)
    by_side: list[dict] = field(default_factory=list)
    by_qty: list[dict] = field(default_factory=list)
    max_loss_streak: int = 0
    ultrashort_count: int = 0
    ultrashort_result: float = 0.0
    period: dict = field(default_factory=dict)


def _num(s: str) -> float | None:
    s = (s or "").strip().replace(".", "").replace(",", ".")
    if s in ("", "-", "- "):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _dt(s: str) -> datetime | None:
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y %H:%M:%S")
    except (ValueError, AttributeError):
        return None


def parse_report(content: bytes) -> list[Trade]:
    """Detecta o cabeçalho 'Ativo;...' e extrai os trades."""
    text = content.decode("latin-1", errors="replace")
    lines = text.splitlines()
    hdr_idx = next(
        (i for i, ln in enumerate(lines) if ln.startswith("Ativo;")), None
    )
    if hdr_idx is None:
        return []
    header = lines[hdr_idx].split(";")
    reader = csv.reader(lines[hdr_idx + 1 :], delimiter=";")
    # índice da coluna de resultado da operação (R$)
    try:
        res_idx = header.index("Res. Operação")
    except ValueError:
        res_idx = 13  # layout padrão Profit/Genial

    trades: list[Trade] = []
    for row in reader:
        if len(row) <= res_idx or not row[0].strip():
            continue
        ab = _dt(row[1])
        fe = _dt(row[2])
        res = _num(row[res_idx])
        if ab is None or fe is None or res is None:
            continue
        qty = int(_num(row[4]) or 1)
        trades.append(
            Trade(
                asset=row[0].strip(),
                abertura=ab,
                fechamento=fe,
                lado=row[6].strip().upper(),
                qty=qty,
                result=res,
                duration_s=(fe - ab).total_seconds(),
            )
        )
    return trades


def compute_metrics(trades: list[Trade]) -> TradeMetrics:
    m = TradeMetrics()
    if not trades:
        return m
    m.total_trades = len(trades)
    wins = [t for t in trades if t.result > 0]
    losses = [t for t in trades if t.result < 0]
    zeros = [t for t in trades if t.result == 0]
    m.wins, m.losses, m.zeros = len(wins), len(losses), len(zeros)
    m.gross_result = round(sum(t.result for t in trades), 2)
    decided = m.wins + m.losses
    m.win_rate = round(m.wins / decided * 100, 1) if decided else 0.0
    gw = sum(t.result for t in wins)
    gl = sum(t.result for t in losses)
    m.avg_win = round(gw / m.wins, 2) if m.wins else 0.0
    m.avg_loss = round(gl / m.losses, 2) if m.losses else 0.0
    m.payoff = round(abs(m.avg_win / m.avg_loss), 2) if m.avg_loss else 0.0
    m.profit_factor = round(gw / abs(gl), 2) if gl else 0.0
    m.best_trade = round(max(t.result for t in trades), 2)
    m.worst_trade = round(min(t.result for t in trades), 2)

    # por dia
    byday: dict = defaultdict(list)
    for t in trades:
        byday[t.abertura.date()].append(t)
    for d in sorted(byday):
        ts = byday[d]
        streak = cur = 0
        for t in sorted(ts, key=lambda x: x.abertura):
            cur = cur + 1 if t.result < 0 else 0
            streak = max(streak, cur)
        m.max_loss_streak = max(m.max_loss_streak, streak)
        m.by_day.append(
            {
                "date": d.isoformat(),
                "trades": len(ts),
                "result": round(sum(x.result for x in ts), 2),
                "wins": len([x for x in ts if x.result > 0]),
                "losses": len([x for x in ts if x.result < 0]),
                "max_qty": max(x.qty for x in ts),
                "loss_streak": streak,
            }
        )

    # por hora
    byh: dict = defaultdict(list)
    for t in trades:
        byh[t.abertura.hour].append(t)
    for h in sorted(byh):
        ts = byh[h]
        m.by_hour.append(
            {
                "hour": h,
                "trades": len(ts),
                "result": round(sum(x.result for x in ts), 2),
                "wins": len([x for x in ts if x.result > 0]),
                "losses": len([x for x in ts if x.result < 0]),
            }
        )

    # por lado
    for lado in ("C", "V"):
        ts = [t for t in trades if t.lado == lado]
        if not ts:
            continue
        w = len([x for x in ts if x.result > 0])
        d = len([x for x in ts if x.result != 0])
        m.by_side.append(
            {
                "side": "Compra" if lado == "C" else "Venda",
                "trades": len(ts),
                "result": round(sum(x.result for x in ts), 2),
                "win_rate": round(w / d * 100, 1) if d else 0.0,
            }
        )

    # por quantidade (mão)
    for q in sorted({t.qty for t in trades}):
        ts = [t for t in trades if t.qty == q]
        w = len([x for x in ts if x.result > 0])
        d = len([x for x in ts if x.result != 0])
        m.by_qty.append(
            {
                "qty": q,
                "trades": len(ts),
                "result": round(sum(x.result for x in ts), 2),
                "win_rate": round(w / d * 100, 1) if d else 0.0,
                "avg": round(sum(x.result for x in ts) / len(ts), 2),
            }
        )

    # ultracurtos
    us = [t for t in trades if t.duration_s <= 30]
    m.ultrashort_count = len(us)
    m.ultrashort_result = round(sum(t.result for t in us), 2)

    m.period = {
        "from": min(t.abertura for t in trades).isoformat(),
        "to": max(t.fechamento for t in trades).isoformat(),
    }
    return m
