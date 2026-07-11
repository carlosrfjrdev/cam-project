"""
Comparador de paridade Python ↔ EA — StrategyLab (R-28/R-29/R-30/R-31).

Dupla checagem independente: alinha o ledger do backtest Python com o ledger
exportado pelo EA, trade-a-trade, e aplica o critério PASS apertado:
  - 100% dos sinais coincidem (mesma barra de entrada, mesmo lado);
  - preço de entrada/saída dentro de `tick_size` (≤ 1 tick);
  - volume financeiro idêntico; qtd idêntica; motivo de saída idêntico.
Qualquer divergência → FAIL (abre BUG). Não "tunar" um lado para casar (R-31).

Determinístico, zero I/O. Consome o schema canônico do ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParityDivergence:
    pair_id: int
    dimension: str   # signal | price_entry | price_exit | qty | volume | exit_reason
    python_value: Any
    ea_value: Any
    hint: str        # item C1-C14 a investigar


@dataclass(frozen=True)
class ParityReport:
    verdict: str                 # PASS | FAIL
    n_python: int
    n_ea: int
    matched: int
    divergences: list[ParityDivergence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "n_python": self.n_python,
            "n_ea": self.n_ea,
            "matched": self.matched,
            "divergences": [
                {
                    "pair_id": d.pair_id,
                    "dimension": d.dimension,
                    "python": d.python_value,
                    "ea": d.ea_value,
                    "hint": d.hint,
                }
                for d in self.divergences
            ],
        }


def _key(trade: dict[str, Any]) -> tuple:
    """Alinha por barra de sinal: (ts_entry, leg/side, symbol)."""
    return (str(trade["ts_entry"]), trade["leg"], trade["symbol"])


def compare(
    python_ledger: list[dict[str, Any]],
    ea_ledger: list[dict[str, Any]],
    tick_size: float,
) -> ParityReport:
    """
    Compara os dois ledgers (lista de dicts no schema canônico). PASS = 100% dos
    sinais coincidem + preços ≤ 1 tick + volume/qtd/motivo idênticos (R-29).
    """
    py_by_key = {_key(t): t for t in python_ledger}
    ea_by_key = {_key(t): t for t in ea_ledger}

    divergences: list[ParityDivergence] = []

    # sinais que existem num lado e não no outro = divergência dura (C1/C3/C4)
    only_py = set(py_by_key) - set(ea_by_key)
    only_ea = set(ea_by_key) - set(py_by_key)
    for k in only_py:
        t = py_by_key[k]
        divergences.append(ParityDivergence(
            t.get("pair_id", -1), "signal", "present", "absent",
            "sinal só no Python — investigar C1/C3/C4 (barra/ordem/fill)"))
    for k in only_ea:
        t = ea_by_key[k]
        divergences.append(ParityDivergence(
            t.get("pair_id", -1), "signal", "absent", "present",
            "sinal só no EA — investigar C1/C3/C4 (barra/ordem/fill)"))

    matched = 0
    for k in set(py_by_key) & set(ea_by_key):
        p, e = py_by_key[k], ea_by_key[k]
        pid = p.get("pair_id", -1)
        ok = True
        if abs(float(p["price_entry"]) - float(e["price_entry"])) > tick_size:
            divergences.append(ParityDivergence(
                pid, "price_entry", p["price_entry"], e["price_entry"],
                "> 1 tick — investigar C4/C5/C6 (fill/intrabar/gap)"))
            ok = False
        if abs(float(p["price_exit"]) - float(e["price_exit"])) > tick_size:
            divergences.append(ParityDivergence(
                pid, "price_exit", p["price_exit"], e["price_exit"],
                "> 1 tick — investigar C5/C6 (intrabar/gap)"))
            ok = False
        if int(p["qty"]) != int(e["qty"]):
            divergences.append(ParityDivergence(
                pid, "qty", p["qty"], e["qty"], "C9 (sizing/arredondamento)"))
            ok = False
        if str(p["exit_reason"]) != str(e["exit_reason"]):
            divergences.append(ParityDivergence(
                pid, "exit_reason", p["exit_reason"], e["exit_reason"],
                "C3/C10/C11 (ordem de avaliação/stop/sessão)"))
            ok = False
        vol_diff = abs(float(p["volume_financeiro"]) - float(e["volume_financeiro"]))
        if vol_diff > tick_size:
            divergences.append(ParityDivergence(
                pid, "volume", p["volume_financeiro"], e["volume_financeiro"],
                "volume divergente — derivado de preço/qtd"))
            ok = False
        if ok:
            matched += 1

    verdict = "PASS" if not divergences else "FAIL"
    return ParityReport(
        verdict=verdict,
        n_python=len(python_ledger),
        n_ea=len(ea_ledger),
        matched=matched,
        divergences=divergences,
    )
