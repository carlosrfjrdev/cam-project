"""
Rebalance Suggestion — TASK-040 (BL-G SPEC v0.4).

Engine de **sugestão** de rebalanceamento de carteira hard. **Nunca executa**
ordens (R-13 + Art. 23). Apenas propõe ações que podem ser exibidas via UI e
enviadas via Telegram.

Critério canônico: target_dy_pct global. Holdings com DY abaixo do alvo
recebem sugestão "VENDER"; holdings com DY acima recebem "COMPRAR".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class RebalanceAction:
    action: str  # "BUY" | "SELL" | "HOLD"
    ticker: str
    delta_qty: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "ticker": self.ticker,
            "delta_qty": self.delta_qty,
            "reason": self.reason,
        }


@dataclass
class RebalanceSuggestion:
    actions: list[RebalanceAction] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "actions": [a.to_dict() for a in self.actions],
            "rationale": self.rationale,
        }


def suggest_rebalance(
    holdings: list[dict[str, Any]],
    fundamentals: dict[str, dict[str, Any]],
    *,
    target_dy: Decimal = Decimal("0.06"),
    deviation_pct: Decimal = Decimal("0.20"),
) -> RebalanceSuggestion:
    """
    Sugere rebalanceamento — não executa.

    Args:
      holdings: lista de holdings (dict com ticker, quantity, avg_price).
      fundamentals: map ticker → snapshot fundamentalista (com dy).
      target_dy: meta global de DY da carteira (POV).
      deviation_pct: margem aceitável em torno do target_dy.

    Returns:
      RebalanceSuggestion com ações HOLD/BUY/SELL.
    """
    actions: list[RebalanceAction] = []
    if not holdings:
        return RebalanceSuggestion(rationale="Sem holdings.")
    upper = target_dy * (Decimal("1") + deviation_pct)
    lower = target_dy * (Decimal("1") - deviation_pct)
    for h in holdings:
        ticker = h.get("ticker", "")
        snap = fundamentals.get(ticker)
        if snap is None or snap.get("dy") is None:
            actions.append(
                RebalanceAction(
                    "HOLD", ticker, 0,
                    "Sem dado fundamentalista — manter.",
                )
            )
            continue
        dy = Decimal(str(snap["dy"]))
        if dy < lower:
            qty = int(Decimal(str(h.get("quantity", 0))) // 2) or 1
            actions.append(
                RebalanceAction(
                    "SELL", ticker, qty,
                    f"DY {dy} < {lower} (abaixo da meta) — reduzir exposição.",
                )
            )
        elif dy > upper:
            qty = int(Decimal(str(h.get("quantity", 0))) // 2) or 1
            actions.append(
                RebalanceAction(
                    "BUY", ticker, qty,
                    f"DY {dy} > {upper} (acima da meta) — aumentar exposição.",
                )
            )
        else:
            actions.append(
                RebalanceAction(
                    "HOLD", ticker, 0,
                    f"DY {dy} dentro da banda alvo.",
                )
            )
    return RebalanceSuggestion(
        actions=actions,
        rationale=f"Target DY={target_dy} ± {deviation_pct * 100}%.",
    )
