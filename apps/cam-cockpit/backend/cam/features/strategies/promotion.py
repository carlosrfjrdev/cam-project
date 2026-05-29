"""
Promotion service — TASK-003 (BL-A).

Promoção de status de estratégia exige `EvidencePack` válido (R1.02).

Fluxo:
  1. Recebe (strategy_id, target_status, evidence_pack).
  2. Persiste EvidencePack em `cam_evidence_packs` (imutável).
  3. Chama repository.update_status (que valida transição monotônica).

Anti-padrões:
  - Promover sem EvidencePack (lança EvidenceRequiredError).
  - Skipar status (lança InvalidStatusTransitionError do repository).
  - Reescrever evidência existente (UNIQUE hash impede dup).
"""
from __future__ import annotations

import json
from datetime import UTC
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cam.features.strategies.domain import StrategyStatus
from cam.features.strategies.evidence import (
    EvidencePack,
    validate_for_target,
)
from cam.features.strategies.repository import StrategyRepository


class EvidenceRequiredError(RuntimeError):
    """Promoção tentada sem EvidencePack."""


class EvidenceDuplicateError(RuntimeError):
    """EvidencePack com mesmo hash já registrado."""


class PromotionService:
    """Orquestra inserção de evidência + transição de status."""

    def __init__(self, repository: StrategyRepository | None = None) -> None:
        self.repository = repository or StrategyRepository()

    async def promote(
        self,
        session: AsyncSession,
        strategy_id: UUID,
        target_status: StrategyStatus,
        evidence: EvidencePack | None,
    ) -> UUID:
        """
        Promove `strategy_id` para `target_status` registrando evidence.

        Retorna o id do EvidencePack persistido.

        Levanta:
          - EvidenceRequiredError se evidence ausente.
          - EvidenceInsufficientError se evidence insuficiente.
          - InvalidStatusTransitionError se transição ilegal.
          - EvidenceDuplicateError se hash já registrado.
          - StrategyNotFoundError se strategy_id ausente.
        """
        # Promoção SEM evidência só é aceita para RETIRED (decisão soberana).
        if target_status is not StrategyStatus.RETIRED and evidence is None:
            raise EvidenceRequiredError(
                f"Promoção para {target_status} exige EvidencePack válido."
            )

        if evidence is not None:
            validate_for_target(evidence)
            evidence_id = await self._persist_evidence(session, evidence)
        else:
            evidence_id = await self._persist_retire_marker(
                session, strategy_id
            )

        await self.repository.update_status(session, strategy_id, target_status)
        return evidence_id

    async def _persist_evidence(
        self,
        session: AsyncSession,
        evidence: EvidencePack,
    ) -> UUID:
        try:
            result = await session.execute(
                text(
                    "INSERT INTO cam_evidence_packs "
                    "(strategy_id, status_target, payload_json, hash) "
                    "VALUES (:sid, :st, CAST(:payload AS jsonb), :hash) "
                    "RETURNING id"
                ),
                {
                    "sid": str(evidence.strategy_id),
                    "st": evidence.status_target.value,
                    "payload": json.dumps(evidence.to_payload()),
                    "hash": evidence.compute_hash(),
                },
            )
            row = result.fetchone()
            await session.commit()
            return UUID(str(row[0]))
        except IntegrityError as err:
            await session.rollback()
            raise EvidenceDuplicateError(
                "EvidencePack com hash duplicado — evidência já registrada."
            ) from err

    async def _persist_retire_marker(
        self,
        session: AsyncSession,
        strategy_id: UUID,
    ) -> UUID:
        """Retire é registro mínimo — payload vazio + hash determinístico."""
        import hashlib
        from datetime import datetime

        # Hash inclui timestamp para permitir múltiplos retires
        # (defensive — retire deveria ser sticky, mas se houver re-registro
        # com mesmo id no futuro o hash não colide).
        nonce = f"retire-{strategy_id}-{datetime.now(UTC).isoformat()}"
        hash_value = hashlib.sha256(nonce.encode("utf-8")).hexdigest()
        result = await session.execute(
            text(
                "INSERT INTO cam_evidence_packs "
                "(strategy_id, status_target, payload_json, hash) "
                "VALUES (:sid, 'retired', '{}'::jsonb, :hash) "
                "RETURNING id"
            ),
            {"sid": str(strategy_id), "hash": hash_value},
        )
        row = result.fetchone()
        await session.commit()
        return UUID(str(row[0]))
