"""
Repository da feature `strategies` — TASK-002 (BL-A).

Operações:
  - register: insere nova estratégia em `cam_strategies` (status=draft, is_active=false).
  - list: lista todas as estratégias ordenadas por created_at.
  - get: busca por id.
  - set_active: troca a estratégia ativa (atômico — desativa anterior, ativa nova).
  - update_status: muda status validando transição (T003 chama).

A constraint `cam_strategies_one_active` garante, em nível de DB, que apenas
uma estratégia esteja ativa por vez. Tentar ativar 2 levanta IntegrityError.

Async via SQLAlchemy 2.0 + psycopg3.
"""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.domain.primitives import AssetType
from cam.features.strategies.domain import (
    StrategyMetadata,
    StrategyStatus,
    is_valid_transition,
)


class StrategyAlreadyExistsError(RuntimeError):
    """Estratégia com mesmo (name, version) já registrada."""


class StrategyNotFoundError(LookupError):
    """Estratégia inexistente no registry."""


class InvalidStatusTransitionError(ValueError):
    """Transição de status proibida (ver `is_valid_transition`)."""


class MultiActiveStrategyError(RuntimeError):
    """
    Tentativa de ativar uma 2ª estratégia enquanto outra está ativa.

    Defesa em profundidade — também enforçada por unique partial index no DB.
    Quando BL-H1 ativar MULTI_STRATEGY_ENABLED=true, este check é relaxado.
    """


class StrategyRepository:
    """
    Acesso assíncrono à tabela `cam_strategies`.

    Mantém-se Stateless — sessão é passada por chamada.
    """

    async def register(
        self,
        session: AsyncSession,
        metadata: StrategyMetadata,
    ) -> UUID:
        """
        Insere nova estratégia em `cam_strategies` no estado `draft`.

        Levanta `StrategyAlreadyExistsError` se (name, version) já existir.
        """
        try:
            result = await session.execute(
                text(
                    "INSERT INTO cam_strategies "
                    "(id, name, version, asset, author, status, is_active, "
                    " metadata_json) "
                    "VALUES (:id, :name, :version, :asset, :author, 'draft', "
                    "        false, CAST(:metadata_json AS jsonb)) "
                    "RETURNING id"
                ),
                {
                    "id": str(metadata.id),
                    "name": metadata.name,
                    "version": metadata.version,
                    "asset": metadata.asset.value,
                    "author": metadata.author,
                    "metadata_json": json.dumps(metadata.custom_metrics),
                },
            )
            row = result.fetchone()
            await session.commit()
            return UUID(str(row[0]))
        except IntegrityError as err:
            await session.rollback()
            raise StrategyAlreadyExistsError(
                f"Estratégia já registrada: {metadata.name} v{metadata.version}"
            ) from err

    async def list_all(self, session: AsyncSession) -> list[dict[str, Any]]:
        """Lista estratégias em ordem cronológica de inserção (ascendente)."""
        result = await session.execute(
            text(
                "SELECT id, name, version, asset, author, status, is_active, "
                "       metadata_json, created_at "
                "FROM cam_strategies "
                "ORDER BY created_at ASC, name ASC"
            )
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get(
        self, session: AsyncSession, strategy_id: UUID
    ) -> dict[str, Any]:
        """Busca por id. Levanta `StrategyNotFoundError` se ausente."""
        result = await session.execute(
            text(
                "SELECT id, name, version, asset, author, status, is_active, "
                "       metadata_json "
                "FROM cam_strategies WHERE id = :id"
            ),
            {"id": str(strategy_id)},
        )
        row = result.fetchone()
        if row is None:
            raise StrategyNotFoundError(str(strategy_id))
        return dict(row._mapping)

    async def set_active(
        self, session: AsyncSession, strategy_id: UUID
    ) -> None:
        """
        Ativa `strategy_id` desativando qualquer outra atualmente ativa.

        Atômico — única transação. Falha se IntegrityError do DB (defesa
        adicional contra concorrência).
        """
        try:
            # 1. desativa todas — passa pela unique partial index sem disparar
            await session.execute(
                text(
                    "UPDATE cam_strategies "
                    "SET is_active = false, updated_at = NOW() "
                    "WHERE is_active = true"
                )
            )
            # 2. ativa a alvo
            result = await session.execute(
                text(
                    "UPDATE cam_strategies "
                    "SET is_active = true, updated_at = NOW() "
                    "WHERE id = :id "
                    "RETURNING id"
                ),
                {"id": str(strategy_id)},
            )
            row = result.fetchone()
            if row is None:
                await session.rollback()
                raise StrategyNotFoundError(str(strategy_id))
            await session.commit()
        except IntegrityError as err:
            await session.rollback()
            raise MultiActiveStrategyError(
                "Constraint cam_strategies_one_active violada — "
                "DB detectou tentativa de ativar 2+ estratégias."
            ) from err

    async def update_status(
        self,
        session: AsyncSession,
        strategy_id: UUID,
        new_status: StrategyStatus,
    ) -> None:
        """
        Muda status validando transição monotônica (`is_valid_transition`).

        TASK-003 (`promotion.py`) chama este método após validar EvidencePack.
        """
        current = await self.get(session, strategy_id)
        current_status = StrategyStatus(current["status"])
        if not is_valid_transition(current_status, new_status):
            raise InvalidStatusTransitionError(
                f"Transição inválida: {current_status} → {new_status}"
            )
        await session.execute(
            text(
                "UPDATE cam_strategies SET status = :s, updated_at = NOW() "
                "WHERE id = :id"
            ),
            {"s": new_status.value, "id": str(strategy_id)},
        )
        await session.commit()

    @staticmethod
    def to_metadata(row: dict[str, Any]) -> StrategyMetadata:
        """Helper: converte row do banco em StrategyMetadata."""
        return StrategyMetadata(
            id=UUID(str(row["id"])),
            name=row["name"],
            version=row["version"],
            asset=AssetType(row["asset"]),
            author=row["author"],
            custom_metrics=row.get("metadata_json") or {},
        )
