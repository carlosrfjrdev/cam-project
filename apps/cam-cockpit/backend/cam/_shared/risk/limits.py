"""
Limites vigentes — TASK-047 (BL-H1 SPEC v0.4).

Substitui constants hardcoded (`MAX_WIN_CONTRACTS = 2`) por leitura do estado
vigente: default (2+2) ou escalonado (BL-H2). `get_current_limits()` é a
ÚNICA fonte canônica de limites em runtime.

⚠️ Cláusula de blindagem (Voltaire 3, EMENDA-001 v2):
    Tetos ABSOLUTOS MAX_SCALED_WIN/WDO/DD declarados em scaling.py (T055).
    Mudanças exigem REVISÃO INTEGRAL — não usar protocolo simplificado v2.0.

Lint Python anti-auto-edição:
    `scripts/lint_constitutional_limits.py` falha CI se PR alterar constants
    fora da allowlist.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

# Default vigente (Art. 11º) — válido quando SCALING_ENABLED=False.
DEFAULT_MAX_WIN_CONTRACTS = 2
DEFAULT_MAX_WDO_CONTRACTS = 2
DEFAULT_MAX_DAILY_DRAWDOWN_PCT = Decimal("0.03")


@dataclass(frozen=True)
class CurrentLimits:
    """Limites vigentes para o pregão atual."""

    max_win: int
    max_wdo: int
    max_daily_drawdown_pct: Decimal
    is_scaled: bool  # True se sob efeito de Art. 11-B
    source: str       # "default" | "scaling_event:<id>"


_runtime_override: CurrentLimits | None = None


def get_current_limits() -> CurrentLimits:
    """
    Retorna limites vigentes. Sem escalonamento ativo → default 2+2.

    BL-H2 (T050 + scaling_job T051) injeta override via `set_current_limits`
    quando uma proposta IN_FORCE estiver vigente no `cam_constitutional_scaling_events`.
    """
    if _runtime_override is not None:
        return _runtime_override
    return CurrentLimits(
        max_win=DEFAULT_MAX_WIN_CONTRACTS,
        max_wdo=DEFAULT_MAX_WDO_CONTRACTS,
        max_daily_drawdown_pct=DEFAULT_MAX_DAILY_DRAWDOWN_PCT,
        is_scaled=False,
        source="default",
    )


def set_current_limits(limits: CurrentLimits | None) -> None:
    """
    Atualiza override em runtime. None → reseta para default.

    USO RESTRITO: chamado apenas por `cam.features.scaling.runtime.apply_event`.
    Lint anti-auto-edição não pega isso por design — runtime é dinâmico.
    """
    global _runtime_override
    _runtime_override = limits
