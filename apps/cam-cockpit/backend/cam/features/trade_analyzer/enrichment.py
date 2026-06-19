"""
Enriquecimento das operações com candles M2 (puro, determinístico).

Para cada trade simula, a partir do horário/preço de entrada e usando os candles
M2 ATÉ O FIM DA SESSÃO:
- Resultado em PONTOS realmente capturado (exit-entry ajustado à direção).
- MFE (excursão favorável máx.) e MAE (adversa máx.) em pontos.
- Desfecho de um setup fixo 1:3 (stop 100 / alvo 300): teria batido ALVO, STOP ou
  nenhum — varrendo candle a candle (pessimista: se alvo e stop no mesmo M2, stop).
- "Mão de alface": ganhou mas deixou muito na mesa (MFE alto vs capturado).

Os números são confiáveis (código); a IA usa o resumo para a narrativa.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from cam.features.trade_analyzer.metrics import Trade

BR_TZ = ZoneInfo("America/Sao_Paulo")
STOP_PTS = 100.0
TARGET_PTS = 300.0  # 1:3
HORIZON_MIN = 120   # janela pós-entrada (min) — realista p/ day trade, capada no EOD
LETTUCE_MIN_MFE = TARGET_PTS  # ganho potencial >= alvo
LETTUCE_MAX_CAPTURED = 150.0  # mas capturou pouco


@dataclass
class TradeEval:
    abertura: str
    direction: str
    entry: float
    exit: float
    result_pts: float
    captured_pts: float
    mfe_pts: float
    mae_pts: float
    rr13: str          # target | stop | none | no_data
    rr13_minutes: float | None
    lettuce: bool      # mão de alface
    left_on_table_pts: float


def _window_end_epoch(entry_dt: datetime) -> float:
    """Fim da janela de análise: entrada + HORIZON_MIN, capado no fim do dia."""
    eod = entry_dt.replace(hour=23, minute=59, second=59).timestamp()
    return min(entry_dt.timestamp() + HORIZON_MIN * 60, eod)


def _simulate(trade: Trade, candles: Sequence[dict]) -> TradeEval:
    entry_dt = trade.abertura.replace(tzinfo=BR_TZ)
    entry_e = entry_dt.timestamp()
    win_end = _window_end_epoch(entry_dt)
    entry = trade.entry_price
    is_long = trade.direction == "LONG"
    captured = (trade.exit_price - entry) if is_long else (entry - trade.exit_price)

    window = [c for c in candles if entry_e <= c["ts"] <= win_end]
    if not entry or not window:
        return TradeEval(
            abertura=entry_dt.isoformat(), direction=trade.direction, entry=entry,
            exit=trade.exit_price, result_pts=round(captured, 1),
            captured_pts=round(captured, 1), mfe_pts=0.0, mae_pts=0.0,
            rr13="no_data", rr13_minutes=None, lettuce=False, left_on_table_pts=0.0,
        )

    if is_long:
        mfe = max(c["h"] for c in window) - entry
        mae = entry - min(c["l"] for c in window)
        target, stop = entry + TARGET_PTS, entry - STOP_PTS
    else:
        mfe = entry - min(c["l"] for c in window)
        mae = max(c["h"] for c in window) - entry
        target, stop = entry - TARGET_PTS, entry + STOP_PTS

    rr13, rr13_min = "none", None
    for c in window:
        hit_target = c["h"] >= target if is_long else c["l"] <= target
        hit_stop = c["l"] <= stop if is_long else c["h"] >= stop
        if hit_target and hit_stop:
            rr13 = "stop"  # pessimista: no mesmo M2, assume stop primeiro
        elif hit_target:
            rr13 = "target"
        elif hit_stop:
            rr13 = "stop"
        if rr13 != "none":
            rr13_min = round((c["ts"] - entry_e) / 60.0, 1)
            break

    lettuce = (
        captured > 0 and mfe >= LETTUCE_MIN_MFE and captured < LETTUCE_MAX_CAPTURED
    )
    left = max(0.0, mfe - captured)
    return TradeEval(
        abertura=entry_dt.isoformat(), direction=trade.direction,
        entry=entry, exit=trade.exit_price, result_pts=round(captured, 1),
        captured_pts=round(captured, 1), mfe_pts=round(mfe, 1), mae_pts=round(mae, 1),
        rr13=rr13, rr13_minutes=rr13_min, lettuce=lettuce,
        left_on_table_pts=round(left, 1),
    )


def enrich(trades: Sequence[Trade], candles: Sequence[dict]) -> dict:
    evals = [_simulate(t, candles) for t in trades]
    with_data = [e for e in evals if e.rr13 != "no_data"]
    n = len(with_data)
    target_hits = sum(1 for e in with_data if e.rr13 == "target")
    stop_hits = sum(1 for e in with_data if e.rr13 == "stop")
    lettuce = [e for e in with_data if e.lettuce]
    return {
        "stop_pts": STOP_PTS,
        "target_pts": TARGET_PTS,
        "trades_avaliados": n,
        "rr13_alvo": target_hits,
        "rr13_stop": stop_hits,
        "rr13_nenhum": n - target_hits - stop_hits,
        "rr13_taxa_alvo_pct": round(target_hits / n * 100, 1) if n else 0.0,
        "mao_de_alface": len(lettuce),
        "pts_deixados_na_mesa": round(sum(e.left_on_table_pts for e in with_data), 1),
        "mfe_medio": round(sum(e.mfe_pts for e in with_data) / n, 1) if n else 0.0,
        "mae_medio": round(sum(e.mae_pts for e in with_data) / n, 1) if n else 0.0,
        "trades": [asdict(e) for e in evals],
    }
