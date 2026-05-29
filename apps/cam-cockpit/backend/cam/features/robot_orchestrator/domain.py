"""
Robot Orchestrator domain — TASK-042 (BL-H1).

Robot = Estratégia(s) + Configuração + Ambiente + Modo de Autonomia (G-R02.01).
Não é IA.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from cam._shared.autonomy.matrix import Env, Mode


class AmbiguousPriorityError(ValueError):
    """Duas estratégias do mesmo robô com mesma prioridade."""


@dataclass(frozen=True)
class StrategyAssignment:
    strategy_id: UUID
    priority: int  # estrita — sem empates dentro de um Robot


@dataclass(frozen=True)
class Robot:
    """
    Robot agrega N estratégias com prioridade estrita.
    """

    id: UUID
    name: str
    env: Env
    mode: Mode
    strategies: tuple[StrategyAssignment, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.strategies:
            raise ValueError(
                f"Robot {self.name!r} sem estratégias — ao menos 1 é exigida."
            )
        priorities = [s.priority for s in self.strategies]
        if len(set(priorities)) != len(priorities):
            raise AmbiguousPriorityError(
                f"Robot {self.name!r} tem prioridades duplicadas: {priorities}"
            )
