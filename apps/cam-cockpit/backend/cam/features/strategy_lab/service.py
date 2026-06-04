"""
Serviço do StrategyLab — orquestra ingest→backtest→métricas→otimização→paridade.

Read-only sobre o live; escreve só em strategy_*. Lê barras de research_bars (já
ingeridas pela Research Lane). MVP de valores BRUTOS (sem custo/IR — R-11). O
otimizador SUGERE (persiste param_set origin='suggested'), nunca aplica (R-08).

NÃO importa mt5_integration nem execução (R-26); NÃO importa _shared.risk no
motor (R-12). A orquestração de EA (Assets Experts) é feita na borda (rota).
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from cam.features.strategy_lab import registry
from cam.features.strategy_lab import repository as repo
from cam.features.strategy_lab.domain import LegTrade, aggregate_by_pair
from cam.features.strategy_lab.metrics import compute_metrics
from cam.features.strategy_lab.optimizer import optimize
from cam.features.strategy_lab.parity import compare

# Rótulo obrigatório em toda saída (MVP bruto — R-11).
GROSS_LABEL = "BRUTO"


# --------------------------------------------------------------------------- #
# Helpers PUROS (testáveis sem banco)
# --------------------------------------------------------------------------- #
def canon_ts(value: Any) -> str:
    """
    Normaliza um timestamp para "YYYY-MM-DDTHH:MM:SS" — formato canônico de
    alinhamento da paridade (o EA emite exatamente este). Aceita datetime ou str.
    """
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    s = str(value).strip().replace(" ", "T").replace("/", "-").replace(".", "-")
    # corta timezone/offset e frações
    s = s.split("+")[0].split("Z")[0]
    if "." in s:
        s = s.split(".")[0]
    # garante segundos
    head = s.split("T")
    if len(head) == 2 and head[1].count(":") == 1:
        s = head[0] + "T" + head[1] + ":00"
    return s


def legs_to_parity_dicts(legs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Converte linhas do ledger (DB ou EA) ao schema do comparador de paridade."""
    out: list[dict[str, Any]] = []
    for t in legs:
        out.append(
            {
                "pair_id": int(t.get("pair_id", -1)),
                "ts_entry": canon_ts(t["ts_entry"]),
                "leg": str(t["leg"]),
                "symbol": str(t["symbol"]),
                "price_entry": float(t["price_entry"]),
                "price_exit": float(t["price_exit"]),
                "qty": int(t["qty"]),
                "exit_reason": str(t["exit_reason"]),
                "volume_financeiro": float(t["volume_financeiro"]),
            }
        )
    return out


def _sharpe_like(pairs: list) -> float:
    """Score Sharpe-like por trade (média/desvio do pnl bruto por par)."""
    pnls = [p.pnl_bruto for p in pairs]
    if len(pnls) < 2:
        return 0.0
    sd = statistics.pstdev(pnls)
    if sd <= 0:
        return 0.0
    return statistics.fmean(pnls) / sd


def _legs_to_rows(run_id: int, legs: list[LegTrade]) -> list[dict[str, Any]]:
    return [
        {
            "run_id": run_id,
            "pair_id": lt.pair_id,
            "leg": lt.leg.value,
            "symbol": lt.symbol,
            "ts_entry": lt.ts_entry,
            "price_entry": lt.price_entry,
            "ts_exit": lt.ts_exit,
            "price_exit": lt.price_exit,
            "qty": lt.qty,
            "exit_reason": lt.exit_reason,
            "pnl_bruto": lt.pnl_bruto,
            "volume_financeiro": lt.volume_financeiro,
        }
        for lt in legs
    ]


# --------------------------------------------------------------------------- #
# Serviço
# --------------------------------------------------------------------------- #
class StrategyLabService:
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        self._factory = session_factory

    # ---- catálogo (Assets Strategy) ----
    def list_strategies(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in registry.list_strategies()]

    def get_strategy(self, strategy_id: str) -> dict[str, Any] | None:
        sd = registry.get(strategy_id)
        return sd.to_dict() if sd else None

    # ---- backtest (Assets RunTests) ----
    async def run_backtest(
        self,
        strategy_id: str,
        symbol: str,
        timeframe: str,
        params: dict[str, Any],
        point_value: float = 0.20,
        qty: int = 1,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        param_set_id: int | None = None,
    ) -> dict[str, Any]:
        sd = registry.get(strategy_id)
        if sd is None or not sd.runnable:
            return {"error": "STRATEGY_NOT_RUNNABLE", "strategy_id": strategy_id}

        async with self._factory() as session:
            # guard de proveniência (T-007): símbolo sem dado → erro explícito.
            n_bars = await repo.symbol_has_data(session, symbol, timeframe)
            if n_bars == 0:
                return {
                    "error": "NO_DATA",
                    "message": (
                        f"Sem barras de {symbol.upper()}/{timeframe} em "
                        "research_bars. Rode a ingestão (Research Lane) antes."
                    ),
                }
            bars = await repo.load_bars(
                session, symbol, timeframe, window_start, window_end
            )
            legs = registry.run(strategy_id, bars, params, point_value, qty)
            metrics = compute_metrics(legs)

            run_id = await repo.create_run(
                session,
                strategy_id=strategy_id,
                symbols=[symbol.upper()],
                unit=sd.unit.value,
                timeframe=timeframe,
                metrics_json=json.dumps(metrics.to_dict()),
                param_set_id=param_set_id,
                window_start=window_start,
                window_end=window_end,
            )
            await repo.insert_legs(session, _legs_to_rows(run_id, legs))
            await session.commit()

        return {
            "run_id": run_id,
            "strategy_id": strategy_id.upper(),
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "mode": "gross",
            "label": GROSS_LABEL,
            "n_bars": len(bars),
            "metrics": metrics.to_dict(),
        }

    # ---- otimizador on-demand (Assets Strategy) ----
    async def run_optimization(
        self,
        strategy_id: str,
        symbol: str,
        timeframe: str,
        space: dict[str, list] | None = None,
        method: str = "grid",
        random_n: int = 50,
        seed: int = 42,
        min_trades: int = 20,
        point_value: float = 0.20,
        qty: int = 1,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
    ) -> dict[str, Any]:
        sd = registry.get(strategy_id)
        if sd is None or not sd.runnable:
            return {"error": "STRATEGY_NOT_RUNNABLE", "strategy_id": strategy_id}
        opt_space = space or sd.param_space
        if not opt_space:
            return {"error": "NO_PARAM_SPACE", "strategy_id": strategy_id}

        async with self._factory() as session:
            n_bars = await repo.symbol_has_data(session, symbol, timeframe)
            if n_bars == 0:
                return {"error": "NO_DATA", "symbol": symbol.upper()}
            bars = await repo.load_bars(
                session, symbol, timeframe, window_start, window_end
            )

            # evaluate roda o backtest IN-MEMORY (sem tocar o banco por trial).
            def evaluate(p: dict[str, Any]) -> tuple[float, int]:
                legs = registry.run(strategy_id, bars, p, point_value, qty)
                pairs = aggregate_by_pair(legs)
                return (_sharpe_like(pairs), len(pairs))

            result = optimize(
                opt_space, evaluate, method=method,
                random_n=random_n, seed=seed, min_trades=min_trades,
            )

            suggestion_id: int | None = None
            if result.verdict == "SUGGEST":
                # persiste a SUGESTÃO (origin='suggested') — não aplica (R-08).
                suggestion_id = await repo.create_param_set(
                    session,
                    strategy_id=strategy_id,
                    params_json=json.dumps(result.best_params),
                    origin="suggested",
                )
                await session.commit()

        return {
            "strategy_id": strategy_id.upper(),
            "symbol": symbol.upper(),
            "verdict": result.verdict,
            "best_params": result.best_params,
            "best_score": (
                None if result.best_score != result.best_score
                else round(result.best_score, 4)
            ),
            "n_trials": result.n_trials,
            "deflated_sharpe": result.deflated_sharpe,
            "no_cliff": result.no_cliff,
            "suggested_param_set_id": suggestion_id,
            "note": "Sugestão — NÃO aplicada automaticamente (R-08).",
        }

    # ---- leitura de resultado (Assets RunTests) ----
    async def get_run(self, run_id: int) -> dict[str, Any] | None:
        async with self._factory() as session:
            run = await repo.get_run(session, run_id)
            if run is None:
                return None
            legs = await repo.get_run_legs(session, run_id)
            return {"run": run, "trades": legs, "label": GROSS_LABEL}

    async def get_equity(self, run_id: int) -> dict[str, Any] | None:
        async with self._factory() as session:
            run = await repo.get_run(session, run_id)
            if run is None:
                return None
            legs = await repo.get_run_legs(session, run_id)
            # Equity por par-como-unidade: soma o pnl_bruto PERSISTIDO (não
            # recalcula — evita divergência de point_value), ordenado por saída.
            pairs: dict[int, dict[str, Any]] = {}
            for t in legs:
                pid = int(t["pair_id"])
                acc = pairs.setdefault(pid, {"pnl": 0.0, "ts_exit": t["ts_exit"]})
                acc["pnl"] += float(t["pnl_bruto"])
                acc["ts_exit"] = max(acc["ts_exit"], t["ts_exit"])
            ordered = sorted(pairs.values(), key=lambda x: x["ts_exit"])
            eq = 0.0
            curve = []
            for it in ordered:
                eq += it["pnl"]
                curve.append(round(eq, 2))
            return {"run_id": run_id, "label": GROSS_LABEL, "equity_curve": curve}

    async def list_runs(
        self, strategy_id: str | None = None
    ) -> list[dict[str, Any]]:
        async with self._factory() as session:
            return await repo.list_runs(session, strategy_id)

    # ---- paridade Python ↔ EA (Assets Experts) ----
    async def run_parity(
        self,
        run_id: int,
        ea_ledger: list[dict[str, Any]],
        tick_size: float,
    ) -> dict[str, Any] | None:
        async with self._factory() as session:
            run = await repo.get_run(session, run_id)
            if run is None:
                return None
            py_legs = await repo.get_run_legs(session, run_id)

        py = legs_to_parity_dicts(py_legs)
        ea = legs_to_parity_dicts(ea_ledger)
        report = compare(py, ea, tick_size=tick_size)
        return {"run_id": run_id, "label": GROSS_LABEL, **report.to_dict()}
