"""
Motor estatístico de trades — CLI standalone.

Roda o pipeline (parse CSV do Profit → métricas → MAE/MFE → grade stop×alvo por
regime) num relatório de operações, fora da tela do cockpit.

Uso:
    python scripts/analyze_trades_motor.py <report.csv> [--candles candles.json]
                                            [--stops 40,60,80,100,120]
                                            [--targets 80,120,200,300,400]
                                            [--min-trades 5] [--json]

- Sem --candles: imprime só as métricas (offline, não precisa de candles).
- Com --candles: arquivo JSON [{"ts":epoch_s,"o","h","l","c"}, ...] (M2 do ativo)
  ou CSV com cabeçalho ts,o,h,l,c. Aí roda o motor completo por regime.

Como obter candles: endpoint GET /api/v1/mt5/candles (backend+bridge de pé) ou
exporte do MT5 e converta para o formato acima.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# permite rodar como `python scripts/analyze_trades_motor.py` a partir do backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cam.features.trade_analyzer.metrics import compute_metrics, parse_report  # noqa: E402
from cam.features.trade_analyzer.motor import run_motor  # noqa: E402


def _load_candles(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
    else:  # CSV com cabeçalho ts,o,h,l,c
        data = list(csv.DictReader(raw.splitlines()))
    out = []
    for r in data:
        out.append(
            {
                "ts": float(r["ts"]),
                "o": float(r.get("o", r.get("c", 0))),
                "h": float(r["h"]),
                "l": float(r["l"]),
                "c": float(r["c"]),
            }
        )
    return out


def _fmt_cell(cell: dict | None) -> str:
    if not cell:
        return "—  (amostra insuficiente)"
    return (
        f"stop {cell['stop_pts']:.0f} / alvo {cell['target_pts']:.0f} "
        f"(R:R {cell['rr']}) | exp {cell['expectancy_pts']:+.1f} pts/trade | "
        f"acerto {cell['win_rate']:.0f}% | PF {cell['profit_factor']} | n={cell['n']}"
    )


def _print_metrics(m) -> None:
    print("=" * 70)
    print(f"OPERAÇÕES: {m.total_trades}  | bruto R$ {m.gross_result:+.2f}  "
          f"| acerto {m.win_rate:.1f}%")
    print(f"ganho médio R$ {m.avg_win:+.2f} | perda média R$ {m.avg_loss:+.2f} "
          f"| payoff {m.payoff} | PF {m.profit_factor}")
    print("=" * 70)


def _print_motor(rep: dict) -> None:
    cob = rep["cobertura"]
    print(f"\nCobertura de candles: {cob['com_candles']}/{cob['total_trades']} "
          f"trades (sem candles: {cob['sem_candles']})")
    print(f"\n>> MELHOR BRACKET GLOBAL: {_fmt_cell(rep['melhor_global'])}")

    print("\n>> POR REGIME (no momento da entrada):")
    for s in rep["por_regime"]:
        print(f"  [{s['segmento']:<16}] n={s['n']:<4} {_fmt_cell(s['melhor'])}")

    print("\n>> STOP QUE SOBREVIVE AO RUÍDO (MAE dos vencedores por regime):")
    for regime, d in rep["mae_vencedores_por_regime"].items():
        print(f"  [{regime:<16}] vencedores={d['n_vencedores']:<4} "
              f"MAE mediana {d['mae_mediana']:.0f} | p75 {d['mae_p75']:.0f} | "
              f"p90 {d['mae_p90']:.0f}  → stop mín sugerido ≥ {d['stop_sugerido_min']:.0f} pts")

    print("\n>> POR HORA:")
    for s in rep["por_hora"]:
        print(f"  [{s['segmento']}] n={s['n']:<4} {_fmt_cell(s['melhor'])}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Motor estatístico de trades (CaM)")
    ap.add_argument("report", help="CSV de operações do Profit")
    ap.add_argument("--candles", help="JSON/CSV de candles M2 do ativo")
    ap.add_argument("--stops", default="40,60,80,100,120,150")
    ap.add_argument("--targets", default="80,120,160,200,300,400")
    ap.add_argument("--min-trades", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="saída JSON crua")
    args = ap.parse_args()

    trades = parse_report(Path(args.report).read_bytes())
    if not trades:
        print("Nenhum trade reconhecido (layout 'Ativo;Abertura;Fechamento;...').")
        return 1
    metrics = compute_metrics(trades)

    if not args.candles:
        if args.json:
            from dataclasses import asdict
            print(json.dumps(asdict(metrics), default=str, ensure_ascii=False, indent=2))
        else:
            _print_metrics(metrics)
            print("\n(Sem --candles: motor por regime não rodou. Forneça candles M2 "
                  "para a tabela stop/alvo por regime.)")
        return 0

    candles = _load_candles(Path(args.candles))
    stops = [float(x) for x in args.stops.split(",")]
    targets = [float(x) for x in args.targets.split(",")]
    rep = run_motor(trades, candles, stops, targets, min_trades=args.min_trades)

    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        _print_metrics(metrics)
        _print_motor(rep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
