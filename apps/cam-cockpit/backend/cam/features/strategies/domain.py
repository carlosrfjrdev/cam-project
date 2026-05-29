"""
Domínio da feature `strategies` — TASK-001 (BL-A, SPEC v0.4-VISION-EVOLUTION).

Contrato canônico de Estratégia plugável no CaM:
  - StrategyStatus: 7 estados do ciclo de vida (draft → retired).
  - is_valid_transition: regra de transição monotônica + retire.
  - StrategyMetadata: dataclass frozen com identidade da estratégia.
  - StrategyContext: snapshot entregue ao evaluate().
  - Strategy: Protocol com `evaluate(tick, context) → OrderCandidate | None`.

Sem persistência (T002 cuida). Sem promoção (T003 cuida).
Vertical slice — esta feature não importa de outras features (ADR-013).

Artigos constitucionais relevantes:
  - Art. 11º: limite absoluto 2 WIN / 2 WDO (validação fica no Risk Engine).
  - Art. 15º: Risk Engine é autoridade — Strategy só propõe.
  - Art. 28º/29º: ciclo de promoção exige evidência (Evidence Pack — T003).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from cam._shared.domain.primitives import AssetType
from cam._shared.risk.context import OrderCandidate


class StrategyStatus(StrEnum):
    """
    Ciclo de vida de uma estratégia. A ordem é monotônica
    (índice maior = mais avançado). `retired` é terminal e absorve qualquer
    estado anterior (qualquer estratégia pode ser aposentada a qualquer momento).
    """

    DRAFT = "draft"
    BACKTESTED = "backtested"
    WALK_FORWARD_OK = "walk_forward_ok"
    PAPER_OK = "paper_ok"
    DEMO_OK = "demo_ok"
    REAL_AUTHORIZED = "real_authorized"
    RETIRED = "retired"


# Ordem monotônica de progressão. RETIRED fica fora — é estado terminal absorvedor.
_STATUS_ORDER: dict[StrategyStatus, int] = {
    StrategyStatus.DRAFT: 0,
    StrategyStatus.BACKTESTED: 1,
    StrategyStatus.WALK_FORWARD_OK: 2,
    StrategyStatus.PAPER_OK: 3,
    StrategyStatus.DEMO_OK: 4,
    StrategyStatus.REAL_AUTHORIZED: 5,
}


def is_valid_transition(current: StrategyStatus, target: StrategyStatus) -> bool:
    """
    Regra de transição:
      - Qualquer estado (exceto RETIRED) pode ir para RETIRED.
      - RETIRED é terminal — não volta.
      - Transições forward só ocorrem em saltos de exatamente +1 na ordem.

    Saltos (ex.: DRAFT → DEMO_OK) são proibidos: cada estado exige evidência.
    """
    if target is StrategyStatus.RETIRED:
        return current is not StrategyStatus.RETIRED
    if current is StrategyStatus.RETIRED:
        return False
    src = _STATUS_ORDER.get(current)
    dst = _STATUS_ORDER.get(target)
    if src is None or dst is None:
        return False
    return dst == src + 1


@dataclass(frozen=True)
class StrategyMetadata:
    """
    Identidade canônica da estratégia. Frozen — qualquer mudança gera nova versão.

    `custom_metrics` carrega parâmetros específicos da estratégia
    (ex.: `opening_range_minutes=60` para S1 ORB).
    """

    id: UUID
    name: str
    version: str
    asset: AssetType
    author: str
    custom_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyContext:
    """
    Snapshot entregue ao `evaluate()`. Carrega tick atual, janela histórica
    relevante para a estratégia e o limite vigente de contratos.

    Strategy **nunca** infere `max_contracts` — sempre lê do contexto. Em produção
    o orquestrador injeta o valor de `get_current_limits()` (BL-H1 T047).
    """

    tick: dict[str, Any]
    history: list[dict[str, Any]] = field(default_factory=list)
    max_contracts: int = 2
    flags: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Strategy(Protocol):
    """
    Contrato canônico de estratégia plugável.

    A função `evaluate` recebe o tick atual + contexto e retorna:
      - `OrderCandidate` se a estratégia detectar oportunidade.
      - `None` em qualquer outro caso (sem sinal).

    O `OrderCandidate` será posteriormente submetido ao Order Gateway (T006)
    que invoca o Risk Engine. A estratégia **não** decide se a ordem será
    enviada — apenas propõe.
    """

    metadata: StrategyMetadata

    def evaluate(
        self, tick: dict[str, Any], context: StrategyContext
    ) -> OrderCandidate | None: ...
