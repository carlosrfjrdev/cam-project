"""
AI Provider Governance — TASK-041 (BL-G SPEC v0.4).

Governa chamadas a providers remotos de IA (Anthropic, OpenAI, Ollama).
OpenAI **bloqueado** até TD-v0.4-02 resolver (ADR + análise custo/anonimização).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class Provider(StrEnum):
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENAI = "openai"


class OpenAINotEnabledError(RuntimeError):
    """OpenAI bloqueado até TD-v0.4-02 (ADR formal)."""


@dataclass(frozen=True)
class ProviderCallRecord:
    id: UUID
    provider: Provider
    model: str
    prompt_hash: str
    response_hash: str
    anonymized: bool
    ts: datetime


def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


async def call_provider(
    provider: Provider | str,
    prompt: str,
    *,
    model: str = "default",
    response: str | None = None,
    anonymized: bool = True,
    session: AsyncSession | None = None,
) -> ProviderCallRecord:
    """
    Chama provider remoto governado.

    Por enquanto trata `response` como string injetada (o teste/caller produz
    via cliente real). OpenAI levanta `OpenAINotEnabledError` sempre.
    """
    if isinstance(provider, str):
        provider = Provider(provider.lower())
    if provider is Provider.OPENAI:
        raise OpenAINotEnabledError(
            "OpenAI bloqueado por TD-v0.4-02 — aguarda ADR formal."
        )

    record = ProviderCallRecord(
        id=uuid4(),
        provider=provider,
        model=model,
        prompt_hash=_hash_text(prompt),
        response_hash=_hash_text(response or ""),
        anonymized=anonymized,
        ts=datetime.now(UTC),
    )
    if session is not None:
        await session.execute(
            text(
                "INSERT INTO cam_ai_provider_calls "
                "(id, provider, model, prompt_hash, response_hash, "
                " anonymized, ts) "
                "VALUES (:id, :p, :m, :ph, :rh, :an, :ts)"
            ),
            {
                "id": str(record.id),
                "p": record.provider.value,
                "m": record.model,
                "ph": record.prompt_hash,
                "rh": record.response_hash,
                "an": record.anonymized,
                "ts": record.ts,
            },
        )
        await session.commit()
    return record
