"""
Robot Orchestrator — TASK-043 (BL-H1).

Distribui tick para todas as estratégias do Robot → coleta candidatos →
chama conflict_resolver → submete vencedores via Order Gateway.

Em modo single-strategy (MULTI_STRATEGY_ENABLED=false), apenas a estratégia
de maior prioridade do Robot é consultada (comportamento legacy preservado).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cam._shared.config import settings
from cam.features.robot_orchestrator.conflict_resolver import (
    ResolutionResult,
    ResolverCandidate,
    resolve,
)
from cam.features.robot_orchestrator.domain import Robot
from cam.features.strategies.domain import Strategy, StrategyContext


@dataclass
class OrchestratorRoundResult:
    candidates_emitted: int = 0
    winners: list[ResolverCandidate] = field(default_factory=list)
    rejected: list[ResolverCandidate] = field(default_factory=list)
    audits: list[tuple[str, str]] = field(default_factory=list)


class RobotOrchestrator:
    """
    Coordena estratégias do Robot por tick.

    `strategy_runtime`: dict strategy_id → callable `evaluate(tick, ctx)`
    (Protocol-compatible).
    `expectancy_lookup`: dict strategy_id → Decimal (média 30d). Para BL-H1
    inicial, caller injeta valores; em produção vem do journal.
    """

    def __init__(
        self,
        robot: Robot,
        strategy_runtime: dict,
        expectancy_lookup: dict,
        suspended_lookup: dict,
    ) -> None:
        self.robot = robot
        self.strategy_runtime = strategy_runtime
        self.expectancy_lookup = expectancy_lookup
        self.suspended_lookup = suspended_lookup

    def handle_tick(
        self,
        tick: dict[str, Any],
        context: StrategyContext,
    ) -> OrchestratorRoundResult:
        """
        Distribui tick para estratégias ativas → resolve conflitos →
        retorna vencedores prontos para serem submetidos via Order Gateway.

        Não chama Order Gateway diretamente — caller compõe pipeline
        completo (orquestrador + risk aggregate + gateway).
        """
        round_result = OrchestratorRoundResult()

        # Single-strategy mode (legacy)
        multi_enabled = getattr(settings, "multi_strategy_enabled", False)
        if not multi_enabled:
            assignments = sorted(
                self.robot.strategies, key=lambda s: s.priority
            )[:1]
        else:
            assignments = sorted(
                self.robot.strategies, key=lambda s: s.priority
            )

        candidates: list[ResolverCandidate] = []
        for assignment in assignments:
            sid = assignment.strategy_id
            if self.suspended_lookup.get(str(sid), False):
                continue
            strat: Strategy | None = self.strategy_runtime.get(str(sid))
            if strat is None:
                continue
            order = strat.evaluate(tick, context)
            if order is None:
                continue
            round_result.candidates_emitted += 1
            candidates.append(
                ResolverCandidate(
                    strategy_id=sid,
                    asset=order.asset,
                    direction=order.direction,
                    contracts=order.contracts.value,
                    expectancy_30d=self.expectancy_lookup.get(
                        str(sid), 0
                    ),
                    is_suspended=False,
                )
            )

        resolution: ResolutionResult = resolve(candidates)
        round_result.winners = resolution.winners
        round_result.rejected = resolution.rejected
        round_result.audits = resolution.audits
        return round_result
