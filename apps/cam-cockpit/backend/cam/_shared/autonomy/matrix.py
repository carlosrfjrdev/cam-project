"""
Autonomy Matrix — TASK-004 (BL-A, SPEC v0.4-VISION-EVOLUTION).

Implementa a tabela G-R02.03 da SPEC: define quais modos de autonomia
(`signal | one_click | semi | full`) são permitidos por ambiente (`backtest |
paper | demo | real`) condicionados ao status da estratégia.

Pure Python, Zero I/O. Risk Engine consome em runtime via Order Gateway (T006).

Regras canônicas:
    | Ambiente | signal | one_click | semi      | full      |
    |----------|--------|-----------|-----------|-----------|
    | backtest | ✅     | N/A       | ✅        | ✅        |
    | paper    | ✅     | ✅        | ✅        | ✅        |
    | demo     | ✅     | ✅        | cond.*    | cond.*    |
    | real     | ✅     | cond.**   | ❌        | ❌        |

    *  condicionado: estratégia em DEMO_OK ou superior.
    ** condicionado forte: status REAL_AUTHORIZED + cooldown 30 dias +
       assinatura simbólica do Founder + REAL_TRADING_ALLOWED=true.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cam.features.strategies.domain import StrategyStatus


class Env(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    DEMO = "demo"
    REAL = "real"


class Mode(StrEnum):
    SIGNAL = "signal"           # Estratégia avisa, sem submeter
    ONE_CLICK = "one_click"     # Operador confirma cada ordem
    SEMI = "semi"               # Auto com janela / horário restrito
    FULL = "full"               # Auto pleno


@dataclass(frozen=True)
class AutonomyContext:
    """
    Contexto consultado para decisões condicionadas.

    Campos:
      real_trading_allowed: feature flag global (TASK-005). False = qualquer
        modo em env=real é bloqueado por design.
      cooldown_passed: True se o cooldown constitucional (30d antes de full
        em real) foi respeitado.
      signature_present: True se o Founder assinou simbolicamente o gate.
    """

    real_trading_allowed: bool = False
    cooldown_passed: bool = False
    signature_present: bool = False


@dataclass(frozen=True)
class AutonomyDecision:
    """Decisão imutável com motivo legível."""

    allowed: bool
    reason: str


# Status mínimo exigido por (env, mode) para liberação básica.
# RETIRED nunca é elegível — bloqueia tudo.
_MIN_STATUS: dict[tuple[Env, Mode], StrategyStatus] = {
    (Env.BACKTEST, Mode.SIGNAL): StrategyStatus.DRAFT,
    (Env.BACKTEST, Mode.SEMI): StrategyStatus.DRAFT,
    (Env.BACKTEST, Mode.FULL): StrategyStatus.DRAFT,
    (Env.PAPER, Mode.SIGNAL): StrategyStatus.DRAFT,
    (Env.PAPER, Mode.ONE_CLICK): StrategyStatus.BACKTESTED,
    (Env.PAPER, Mode.SEMI): StrategyStatus.BACKTESTED,
    (Env.PAPER, Mode.FULL): StrategyStatus.BACKTESTED,
    (Env.DEMO, Mode.SIGNAL): StrategyStatus.PAPER_OK,
    (Env.DEMO, Mode.ONE_CLICK): StrategyStatus.PAPER_OK,
    (Env.DEMO, Mode.SEMI): StrategyStatus.DEMO_OK,
    (Env.DEMO, Mode.FULL): StrategyStatus.DEMO_OK,
    (Env.REAL, Mode.SIGNAL): StrategyStatus.DEMO_OK,
    (Env.REAL, Mode.ONE_CLICK): StrategyStatus.REAL_AUTHORIZED,
}


def is_mode_allowed(
    env: Env,
    mode: Mode,
    strategy_status: StrategyStatus,
    context: AutonomyContext | None = None,
) -> AutonomyDecision:
    """
    Avalia se `(env, mode)` é permitido para uma estratégia com `strategy_status`.

    Decisão retornada inclui motivo legível (útil em audit logs).

    Regras especiais:
      - RETIRED: bloqueia tudo.
      - BACKTEST + ONE_CLICK: combinação inexistente (N/A na matriz).
      - REAL + SEMI/FULL: vedado até gate futuro (Anexo II + decisão Founder).
      - REAL + ONE_CLICK: condicionado forte — exige cooldown + assinatura +
        real_trading_allowed=True.
    """
    ctx = context or AutonomyContext()

    # 1. RETIRED bloqueia tudo
    if strategy_status is StrategyStatus.RETIRED:
        return AutonomyDecision(
            allowed=False,
            reason="Estratégia em RETIRED — qualquer execução bloqueada.",
        )

    # 2. BACKTEST + ONE_CLICK: N/A
    if env is Env.BACKTEST and mode is Mode.ONE_CLICK:
        return AutonomyDecision(
            allowed=False,
            reason=(
                "Modo ONE_CLICK não se aplica em BACKTEST "
                "(sem confirmação ao vivo)."
            ),
        )

    # 3. REAL + SEMI / REAL + FULL: vedado até gate futuro
    if env is Env.REAL and mode in (Mode.SEMI, Mode.FULL):
        return AutonomyDecision(
            allowed=False,
            reason=(
                "REAL + (SEMI|FULL) vedado nesta SPEC. "
                "Liberação exige decisão futura do Founder (Anexo II)."
            ),
        )

    # 4. Real-trading-allowed gate
    if env is Env.REAL and not ctx.real_trading_allowed:
        return AutonomyDecision(
            allowed=False,
            reason="REAL_TRADING_ALLOWED=false — operação real bloqueada por design.",
        )

    # 5. Status mínimo
    min_status = _MIN_STATUS.get((env, mode))
    if min_status is None:
        return AutonomyDecision(
            allowed=False,
            reason=f"Combinação ({env}, {mode}) não está na matriz canônica.",
        )

    if _status_rank(strategy_status) < _status_rank(min_status):
        return AutonomyDecision(
            allowed=False,
            reason=(
                f"Status insuficiente: estratégia em {strategy_status}, "
                f"mínimo exigido para ({env}, {mode}) é {min_status}."
            ),
        )

    # 6. REAL + ONE_CLICK exige condicionamento forte adicional
    if env is Env.REAL and mode is Mode.ONE_CLICK:
        if not ctx.cooldown_passed:
            return AutonomyDecision(
                allowed=False,
                reason=(
                    "REAL + ONE_CLICK exige cooldown 30 dias respeitado "
                    "(condicionado forte)."
                ),
            )
        if not ctx.signature_present:
            return AutonomyDecision(
                allowed=False,
                reason=(
                    "REAL + ONE_CLICK exige assinatura simbólica do Founder "
                    "(condicionado forte)."
                ),
            )

    # 7. DEMO + (SEMI|FULL) exige cooldown (condicionado)
    if env is Env.DEMO and mode in (Mode.SEMI, Mode.FULL):
        if not ctx.cooldown_passed:
            return AutonomyDecision(
                allowed=False,
                reason=(
                    f"DEMO + {mode} é condicionado: cooldown ainda não cumprido."
                ),
            )

    return AutonomyDecision(allowed=True, reason="ok")


_RANK = {
    StrategyStatus.DRAFT: 0,
    StrategyStatus.BACKTESTED: 1,
    StrategyStatus.WALK_FORWARD_OK: 2,
    StrategyStatus.PAPER_OK: 3,
    StrategyStatus.DEMO_OK: 4,
    StrategyStatus.REAL_AUTHORIZED: 5,
    StrategyStatus.RETIRED: -1,
}


def _status_rank(s: StrategyStatus) -> int:
    return _RANK[s]
