"""
Strategy Escalation Engine — TASK-050 + TASK-055 (BL-H2 SPEC v0.4).

Art. 11-B — Escalonamento condicional do limite do Art. 11º.

**Pure Python, sem auto-execução**. Calcula elegibilidade dado um snapshot
de 30 pregões; **não persiste**; **não aplica**. T051 (job) chama em batch,
T052 persiste, T053 endpoint aplica via ESC-NNN manual.

⚠️ Cláusula de blindagem (Voltaire 3):
    `MAX_SCALED_WIN`, `MAX_SCALED_WDO` e `MAX_DAILY_DRAWDOWN_PCT` são
    TETOS ABSOLUTOS. Emendas que mexam neles **exigem REVISÃO INTEGRAL**
    (não protocolo simplificado v2.0 — ver PROTOCOLO-EMENDA-CONSTITUCIONAL.md).

⚠️ Lint anti-auto-edição:
    `scripts/lint_constitutional_limits.py` falha CI se PR alterar essas
    constants fora de allowlist explícita.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

# =============================================================================
# TETOS ABSOLUTOS — CLÁUSULA DE BLINDAGEM (Voltaire 3, EMENDA-001 v2)
# =============================================================================
# Emendas que mexam nesses tetos EXIGEM REVISÃO INTEGRAL (não protocolo
# simplificado v2.0). Lint Python anti-auto-edição barra alteração em PR.
MAX_SCALED_WIN: int = 5
MAX_SCALED_WDO: int = 5
MAX_DAILY_DRAWDOWN_PCT: Decimal = Decimal("0.03")
# =============================================================================


# Pisos dos 5 critérios (Art. 11-B item a)
PROFIT_FACTOR_MIN = Decimal("1.8")
WIN_RATE_MIN = Decimal("0.55")
EXPECTANCY_MULTIPLE_OF_COST_MIN = Decimal("1.5")
DRAWDOWN_MAX_PCT = Decimal("0.10")  # 10% do Bucket Derivativo
ADHERENCE_MIN = Decimal("0.95")
EVALUATION_WINDOW_PREGOES = 30


@dataclass(frozen=True)
class ScalingEvidence:
    profit_factor: Decimal
    win_rate: Decimal
    expectancy_net: Decimal
    monthly_fixed_cost: Decimal
    drawdown_pct: Decimal
    adherence: Decimal
    pregoes_count: int
    prev_period_was_scaled: bool = False  # Voltaire 2: DD em dobro

    def to_dict(self) -> dict[str, Any]:
        return {
            "profit_factor": str(self.profit_factor),
            "win_rate": str(self.win_rate),
            "expectancy_net": str(self.expectancy_net),
            "monthly_fixed_cost": str(self.monthly_fixed_cost),
            "drawdown_pct": str(self.drawdown_pct),
            "adherence": str(self.adherence),
            "pregoes_count": self.pregoes_count,
            "prev_period_was_scaled": self.prev_period_was_scaled,
        }


@dataclass(frozen=True)
class ScalingEligibility:
    eligible: bool
    evidence: ScalingEvidence
    missing_criteria: list[str] = field(default_factory=list)


def compute_scaling_eligibility(evidence: ScalingEvidence) -> ScalingEligibility:
    """
    Avalia 5 critérios (Art. 11-B item a) + janela de 30 pregões.

    Voltaire 2: se `prev_period_was_scaled=True`, drawdown é **dobrado**
    na avaliação atual.
    """
    missing: list[str] = []

    if evidence.pregoes_count < EVALUATION_WINDOW_PREGOES:
        missing.append(
            f"pregoes_count={evidence.pregoes_count} < {EVALUATION_WINDOW_PREGOES}"
        )

    if evidence.profit_factor < PROFIT_FACTOR_MIN:
        missing.append(
            f"profit_factor={evidence.profit_factor} < {PROFIT_FACTOR_MIN}"
        )

    if evidence.win_rate < WIN_RATE_MIN:
        missing.append(f"win_rate={evidence.win_rate} < {WIN_RATE_MIN}")

    expectancy_threshold = (
        evidence.monthly_fixed_cost * EXPECTANCY_MULTIPLE_OF_COST_MIN
    )
    if evidence.expectancy_net < expectancy_threshold:
        missing.append(
            f"expectancy_net={evidence.expectancy_net} < {expectancy_threshold} "
            f"(={EXPECTANCY_MULTIPLE_OF_COST_MIN}× cost {evidence.monthly_fixed_cost})"
        )

    # Voltaire 2: DD em dobro se período anterior foi escalonado
    effective_dd = (
        evidence.drawdown_pct * Decimal("2")
        if evidence.prev_period_was_scaled
        else evidence.drawdown_pct
    )
    if effective_dd > DRAWDOWN_MAX_PCT:
        missing.append(
            f"drawdown={effective_dd} > {DRAWDOWN_MAX_PCT} "
            f"(prev_scaled={evidence.prev_period_was_scaled} → dobrado)"
        )

    if evidence.adherence < ADHERENCE_MIN:
        missing.append(f"adherence={evidence.adherence} < {ADHERENCE_MIN}")

    return ScalingEligibility(
        eligible=len(missing) == 0,
        evidence=evidence,
        missing_criteria=missing,
    )


# ---------------------------------------------------------------------------
# Incremento +1 estrito (Marty)
# ---------------------------------------------------------------------------
class IncrementalViolationError(ValueError):
    """Tentativa de salto +2 ou maior — Art. 11-B exige incremento estrito +1."""


class BlockedByCeilingError(ValueError):
    """Tentativa de exceder MAX_SCALED_WIN/MAX_SCALED_WDO — teto absoluto."""


def validate_incremental_step(
    asset: str, current_limit: int, proposed_limit: int
) -> None:
    """
    Aceita apenas (current + 1). Rejeita (current + 2) ou maior.
    Recusa também propostas que excedam tetos absolutos (T055).
    """
    if proposed_limit != current_limit + 1:
        raise IncrementalViolationError(
            f"Salto inválido: {current_limit} → {proposed_limit}. "
            f"Incremento permitido: +1 estrito (Art. 11-B + Marty 1)."
        )

    ceiling = (
        MAX_SCALED_WIN if asset.upper() == "WIN" else MAX_SCALED_WDO
    )
    if proposed_limit > ceiling:
        raise BlockedByCeilingError(
            f"{asset} proposto {proposed_limit} excede teto absoluto {ceiling}. "
            "Cláusula de blindagem Voltaire 3: revisão integral exigida."
        )


# ---------------------------------------------------------------------------
# Cooldown reverso (Voltaire 1)
# ---------------------------------------------------------------------------
COOLDOWN_DEFAULT_DAYS = 7
COOLDOWN_WIN_STREAK_DAYS = 21
WIN_STREAK_THRESHOLD = 5  # 5 wins consecutivos = streak


def detect_win_streak(consecutive_wins: int) -> bool:
    return consecutive_wins >= WIN_STREAK_THRESHOLD


def compute_cooldown_days(consecutive_wins: int) -> int:
    """7d padrão; 21d se win streak ativo (Voltaire 1)."""
    return (
        COOLDOWN_WIN_STREAK_DAYS
        if detect_win_streak(consecutive_wins)
        else COOLDOWN_DEFAULT_DAYS
    )
