"""
Order Gateway — TASK-006 (BL-A, SPEC v0.4-VISION-EVOLUTION).

SEC-CRÍTICO — Único caminho de ordem do CaM. Toda ordem (paper, demo, real)
**DEVE** passar por `submit()`. Caminhos paralelos são vedados pela SPEC
(princípio global G-R01.01 + R1.07).

Pipeline obrigatório, em ordem:

    1. real_trading_flag_check (CA-A.8)
    2. autonomy_check          (CA-A.4)
    3. idempotency_check
    4. risk_validate           (CA-A.7 — Art. 15º)
    5. audit                   (Art. 31º)
    6. dispatch                (paper | EA via BL-E T028)

Sem `risk_validate` aprovado → **não** dispatcha.
Sem `real_trading_allowed=True` e `env=real` → `RealTradingDisabledError`.

`EADispatcher` aqui é placeholder — implementação concreta em T028 (BL-E).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

import structlog

from cam._shared.autonomy.matrix import (
    AutonomyContext,
    Env,
    Mode,
    is_mode_allowed,
)
from cam._shared.config import Settings
from cam._shared.risk import (
    Approved,
    OrderCandidate,
    Rejected,
    RiskContext,
)
from cam._shared.risk import (
    validate as risk_validate,
)
from cam.features.strategies.domain import StrategyStatus

logger = structlog.get_logger("cam.order_gateway")


# ---------------------------------------------------------------------------
# Exceções específicas
# ---------------------------------------------------------------------------
class RealTradingDisabledError(RuntimeError):
    """env=real bloqueado por `real_trading_allowed=False`."""


class AutonomyBlockedError(RuntimeError):
    """Autonomy Matrix bloqueou a combinação (env, mode, status)."""


class DuplicateIntentError(RuntimeError):
    """Mesma `idempotency_key` submetida duas vezes na janela de cache."""


class BridgeUnavailableError(RuntimeError):
    """EADispatcher chamado sem bridge configurada (BL-E T028 implementa)."""


# ---------------------------------------------------------------------------
# Dispatcher Protocols
# ---------------------------------------------------------------------------
class PaperDispatcher(Protocol):
    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]: ...


class EADispatcher(Protocol):
    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]: ...


class _NullEADispatcher:
    """Placeholder — substituído por implementação real em T028 (BL-E)."""

    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]:
        raise BridgeUnavailableError(
            "EADispatcher ainda não implementado — chega em BL-E T028."
        )


class _LocalPaperDispatcher:
    """Dispatcher paper default — simulação imediata (sem fill real)."""

    async def dispatch(
        self, candidate: OrderCandidate, idempotency_key: UUID
    ) -> dict[str, Any]:
        return {
            "status": "simulated",
            "asset": candidate.asset.value,
            "direction": candidate.direction.value,
            "contracts": candidate.contracts.value,
            "idempotency_key": str(idempotency_key),
        }


# ---------------------------------------------------------------------------
# Resultado da submissão
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OrderResult:
    """Resultado da submissão. Frozen — caller persiste em audit/journal."""

    approved: bool
    decision: str  # "APPROVED" | "REJECTED"
    reason: str
    validator: str | None = None
    dispatch_payload: dict[str, Any] | None = None
    idempotency_key: UUID | None = None


# ---------------------------------------------------------------------------
# Idempotency cache (em memória, TTL=60s)
# ---------------------------------------------------------------------------
class _IdempotencyCache:
    """Cache simples em memória. Em produção: Redis ou tabela DB."""

    TTL_SECONDS = 60

    def __init__(self) -> None:
        self._seen: dict[UUID, datetime] = {}

    def check_and_mark(self, key: UUID) -> bool:
        """Retorna True se chave **nova**; False se já vista na janela TTL."""
        self._purge()
        if key in self._seen:
            return False
        self._seen[key] = datetime.now(UTC)
        return True

    def _purge(self) -> None:
        now = datetime.now(UTC)
        expired = [
            k for k, ts in self._seen.items()
            if (now - ts).total_seconds() > self.TTL_SECONDS
        ]
        for k in expired:
            del self._seen[k]


# ---------------------------------------------------------------------------
# OrderGateway
# ---------------------------------------------------------------------------
@dataclass
class OrderGateway:
    """
    Coordenador único de ordens. Stateless quanto a contexto operacional —
    apenas o `_IdempotencyCache` mantém estado de curtíssima duração.

    Construção típica em produção:

        gateway = OrderGateway(
            settings=settings,
            paper=LocalPaperDispatcher(),
            ea=_NullEADispatcher(),     # substitui em BL-E T028
        )
    """

    settings: Settings
    paper: PaperDispatcher = field(default_factory=_LocalPaperDispatcher)
    ea: EADispatcher = field(default_factory=_NullEADispatcher)
    _cache: _IdempotencyCache = field(default_factory=_IdempotencyCache)

    async def submit(
        self,
        *,
        candidate: OrderCandidate,
        risk_context: RiskContext,
        env: Env,
        mode: Mode,
        strategy_status: StrategyStatus,
        idempotency_key: UUID,
        autonomy_context: AutonomyContext | None = None,
    ) -> OrderResult:
        """
        Submete uma intenção de ordem. Encadeia todas as defesas constitucionais.

        Retorna OrderResult — caller persiste em `cam_risk_decisions` (Art. 31º).
        """
        # ---- 1. REAL_TRADING_ALLOWED — gate por design ----
        if env is Env.REAL and not self.settings.real_trading_allowed:
            await self._audit("real_trading_disabled", candidate, env, mode)
            return OrderResult(
                approved=False,
                decision="REJECTED",
                reason="REAL_TRADING_ALLOWED=false — operação real travada por design.",
                validator="real_trading_flag",
                idempotency_key=idempotency_key,
            )

        # ---- 2. Autonomy Matrix ----
        autonomy = is_mode_allowed(
            env=env,
            mode=mode,
            strategy_status=strategy_status,
            context=autonomy_context or AutonomyContext(
                real_trading_allowed=self.settings.real_trading_allowed,
            ),
        )
        if not autonomy.allowed:
            await self._audit(
                "autonomy_blocked", candidate, env, mode, reason=autonomy.reason
            )
            return OrderResult(
                approved=False,
                decision="REJECTED",
                reason=autonomy.reason,
                validator="autonomy_matrix",
                idempotency_key=idempotency_key,
            )

        # ---- 3. Idempotency ----
        if not self._cache.check_and_mark(idempotency_key):
            await self._audit(
                "duplicate_intent", candidate, env, mode,
                reason=f"key={idempotency_key} duplicada na janela TTL"
            )
            return OrderResult(
                approved=False,
                decision="REJECTED",
                reason="Idempotency key duplicada — possível retry indevido.",
                validator="idempotency",
                idempotency_key=idempotency_key,
            )

        # ---- 4. Risk Engine (Art. 15º) ----
        decision = risk_validate(candidate, risk_context)
        if isinstance(decision, Rejected):
            await self._audit(
                "risk_rejected", candidate, env, mode,
                reason=decision.reason, validator=decision.validator,
            )
            return OrderResult(
                approved=False,
                decision="REJECTED",
                reason=decision.reason,
                validator=decision.validator,
                idempotency_key=idempotency_key,
            )

        assert isinstance(decision, Approved)

        # ---- 5. Dispatch ----
        try:
            if env is Env.PAPER or env is Env.BACKTEST:
                payload = await self.paper.dispatch(candidate, idempotency_key)
            else:  # demo / real
                payload = await self.ea.dispatch(candidate, idempotency_key)
        except BridgeUnavailableError as err:
            await self._audit(
                "dispatch_unavailable", candidate, env, mode,
                reason=str(err),
            )
            return OrderResult(
                approved=False,
                decision="REJECTED",
                reason=str(err),
                validator="dispatcher",
                idempotency_key=idempotency_key,
            )

        # ---- 6. Audit final ----
        await self._audit(
            "approved_and_dispatched", candidate, env, mode,
            reason="Pipeline completo aprovou ordem.",
        )

        return OrderResult(
            approved=True,
            decision="APPROVED",
            reason="ok",
            validator=None,
            dispatch_payload=payload,
            idempotency_key=idempotency_key,
        )

    async def _audit(
        self,
        op_event: str,
        candidate: OrderCandidate,
        env: Env,
        mode: Mode,
        *,
        reason: str = "",
        validator: str | None = None,
    ) -> None:
        """
        Audit estruturado (Art. 31º). Pure log — persistência mais robusta
        (cam_audit_events) entra em SPEC futura.
        """
        logger.info(
            "order_gateway_event",
            op_event=op_event,
            env=str(env),
            mode=str(mode),
            asset=str(candidate.asset),
            direction=str(candidate.direction),
            contracts=candidate.contracts.value,
            reason=reason,
            validator=validator,
        )
