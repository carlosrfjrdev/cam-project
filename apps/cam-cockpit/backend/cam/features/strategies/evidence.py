"""
EvidencePack — TASK-003 (BL-A).

Snapshot serializável de evidência para promoção de status de estratégia.
Cada `status_target` exige um EvidencePack com critérios mínimos satisfeitos.

Mínimos do BL-A:
  - BACKTESTED: ≥ 1 backtest_run + drawdown reportado.
  - WALK_FORWARD_OK: ≥ 1 walk_forward_result.
  - PAPER_OK: ≥ 100 paper_results + aderência ≥ 0.95. (validação em T019)

Estrutura imutável (frozen). Hash determinístico via SHA-256 sobre o payload
ordenado canonicamente.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from cam.features.strategies.domain import StrategyStatus


@dataclass(frozen=True)
class EvidencePack:
    """
    Evidência consolidada para promoção de estratégia.

    Campos:
      strategy_id: estratégia alvo.
      status_target: status pretendido (não pode ser DRAFT).
      backtest_runs: lista de ids/refs de backtest runs.
      walk_forward_results: resultados de walk-forward.
      paper_results: ids de paper trades (T019 valida ≥ 100).
      adherence: aderência média (0.0 a 1.0).
      drawdown: drawdown máximo observado (BRL).
      expectancy_net: expectância líquida (BRL).
      custom_metrics: métricas adicionais específicas da estratégia.
    """

    strategy_id: UUID
    status_target: StrategyStatus
    backtest_runs: list[str] = field(default_factory=list)
    walk_forward_results: list[str] = field(default_factory=list)
    paper_results: list[str] = field(default_factory=list)
    adherence: Decimal = Decimal("0")
    drawdown: Decimal = Decimal("0")
    expectancy_net: Decimal = Decimal("0")
    custom_metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status_target is StrategyStatus.DRAFT:
            raise ValueError(
                "EvidencePack não promove para DRAFT — estado inicial."
            )

    def to_payload(self) -> dict[str, Any]:
        """
        Payload serializável (JSONB). Decimal → str para preservar precisão.
        """
        return {
            "strategy_id": str(self.strategy_id),
            "status_target": self.status_target.value,
            "backtest_runs": list(self.backtest_runs),
            "walk_forward_results": list(self.walk_forward_results),
            "paper_results": list(self.paper_results),
            "adherence": str(self.adherence),
            "drawdown": str(self.drawdown),
            "expectancy_net": str(self.expectancy_net),
            "custom_metrics": dict(self.custom_metrics),
        }

    def compute_hash(self) -> str:
        """
        Hash SHA-256 sobre o payload com keys ordenadas — determinístico.
        Usado como UNIQUE constraint em `cam_evidence_packs.hash`.
        """
        payload = json.dumps(self.to_payload(), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Validações de pré-requisitos por status alvo
# ---------------------------------------------------------------------------
class EvidenceInsufficientError(ValueError):
    """Evidência presente mas não satisfaz pré-requisitos do status alvo."""


def validate_for_target(pack: EvidencePack) -> None:
    """
    Valida pré-requisitos mínimos por status alvo.

    Lança EvidenceInsufficientError se evidência inadequada.
    Promoção `paper_ok` exige validação adicional em T019 (≥ 100 trades +
    aderência ≥ 95%) — aqui validamos apenas presença mínima.
    """
    target = pack.status_target

    if target is StrategyStatus.BACKTESTED:
        if not pack.backtest_runs:
            raise EvidenceInsufficientError(
                "Promoção para BACKTESTED exige ≥ 1 backtest_run"
            )

    elif target is StrategyStatus.WALK_FORWARD_OK:
        if not pack.walk_forward_results:
            raise EvidenceInsufficientError(
                "Promoção para WALK_FORWARD_OK exige ≥ 1 walk_forward_result"
            )

    elif target is StrategyStatus.PAPER_OK:
        # T019 valida 100 trades + aderência. Aqui exige presença mínima.
        if not pack.paper_results:
            raise EvidenceInsufficientError(
                "Promoção para PAPER_OK exige paper_results (T019 valida 100+)"
            )

    elif target is StrategyStatus.DEMO_OK:
        if not pack.paper_results:
            raise EvidenceInsufficientError(
                "Promoção para DEMO_OK exige histórico de paper consolidado"
            )

    elif target is StrategyStatus.REAL_AUTHORIZED:
        # Gate manual do Founder — aqui só exigimos evidência de demo.
        if pack.adherence < Decimal("0.95"):
            raise EvidenceInsufficientError(
                "Promoção para REAL_AUTHORIZED exige adherence ≥ 0.95"
            )

    # RETIRED não exige evidência além do registro do motivo nos custom_metrics.
