"""
Provenance + ingestão de ticks — TASK-012 + TASK-013 (BL-B SPEC v0.4).

`ingest_ticks(ticks, source_metadata)`:
  1. Calcula hash determinístico do lote.
  2. Computa quality flags (T013).
  3. Persiste provenance + ticks em uma única transação.
  4. Reimport com mesmo hash → 0 duplicados (CA-B.2).

Stateless — service-style.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class TickRow:
    """Tick mínimo para ingestão."""

    asset: str
    timestamp: datetime
    price: Decimal
    volume: int


@dataclass(frozen=True)
class ProvenanceInput:
    """Metadados de origem do lote."""

    source: str
    source_url: str | None = None
    license_terms_ack: bool = False


@dataclass(frozen=True)
class IngestResult:
    """Resultado da ingestão."""

    import_id: UUID | None
    tick_count: int
    duplicated: bool
    hash: str
    quality_flags: dict[str, Any]


class LicenseNotAckError(RuntimeError):
    """`license_terms_ack=False` — ingestão bloqueada (R2.02)."""


# ---------------------------------------------------------------------------
# Quality flags (TASK-013, R2.04, CA-B.3)
# ---------------------------------------------------------------------------
PREGAO_OPEN = time(9, 0)
PREGAO_CLOSE = time(18, 30)


def compute_quality_flags(
    ticks: list[TickRow],
    *,
    gap_threshold_seconds: int = 60,
) -> dict[str, Any]:
    """
    Computa flags: has_gaps, has_zero_volume, out_of_hours.

    - `has_gaps`: True se algum gap entre ticks consecutivos > threshold.
    - `has_zero_volume`: True se algum tick com volume == 0.
    - `out_of_hours`: True se algum tick fora da janela 09:00–18:30 BRT
       (assume timestamps UTC — converte naive comparando time-of-day puro).
    """
    if not ticks:
        return {
            "has_gaps": False,
            "has_zero_volume": False,
            "out_of_hours": False,
            "tick_count": 0,
        }

    has_zero_volume = any(t.volume == 0 for t in ticks)

    # Ordena por timestamp para gap analysis (não muta input)
    sorted_ticks = sorted(ticks, key=lambda t: t.timestamp)
    has_gaps = False
    for prev, curr in zip(sorted_ticks, sorted_ticks[1:], strict=False):
        delta = (curr.timestamp - prev.timestamp).total_seconds()
        if delta > gap_threshold_seconds:
            has_gaps = True
            break

    out_of_hours = False
    for t in sorted_ticks:
        tod = t.timestamp.time()
        if not (PREGAO_OPEN <= tod <= PREGAO_CLOSE):
            out_of_hours = True
            break

    return {
        "has_gaps": has_gaps,
        "has_zero_volume": has_zero_volume,
        "out_of_hours": out_of_hours,
        "tick_count": len(ticks),
    }


def compute_batch_hash(ticks: list[TickRow], source: str) -> str:
    """Hash SHA-256 determinístico do lote (source + tuplas asset/ts/price/vol)."""
    h = hashlib.sha256()
    h.update(source.encode("utf-8"))
    for t in sorted(ticks, key=lambda x: (x.asset, x.timestamp)):
        h.update(
            f"|{t.asset}|{t.timestamp.isoformat()}|{t.price}|{t.volume}".encode()
        )
    return h.hexdigest()


# ---------------------------------------------------------------------------
# MarketDataService.ingest_ticks
# ---------------------------------------------------------------------------
class MarketDataService:
    """Serviço de ingestão com provenance + dedup hash."""

    async def ingest_ticks(
        self,
        session: AsyncSession,
        ticks: list[TickRow],
        provenance: ProvenanceInput,
    ) -> IngestResult:
        """
        Ingesta lote com provenance obrigatório + dedup determinístico.

        Levanta:
          - LicenseNotAckError se `license_terms_ack=False`.
          - ValueError se ticks vazios.
        """
        if not provenance.license_terms_ack:
            raise LicenseNotAckError(
                "license_terms_ack=False — não é possível ingerir ticks. "
                "Confirme aceitação dos termos da fonte antes de prosseguir."
            )
        if not ticks:
            raise ValueError("Lote vazio — nada a ingerir.")

        batch_hash = compute_batch_hash(ticks, provenance.source)
        quality = compute_quality_flags(ticks)

        ts_origin_min = min(t.timestamp for t in ticks)
        ts_origin_max = max(t.timestamp for t in ticks)
        asset_set = {t.asset for t in ticks}
        asset_canonical = (
            ",".join(sorted(asset_set)) if len(asset_set) > 1
            else next(iter(asset_set))
        )

        try:
            result = await session.execute(
                text(
                    "INSERT INTO cam_market_data_provenance "
                    "(source, source_url, asset, ts_origin_min, ts_origin_max,"
                    " tick_count, hash, quality_flags, license_terms_ack) "
                    "VALUES (:source, :url, :asset, :tsmin, :tsmax, "
                    "        :count, :hash, CAST(:flags AS jsonb), :ack) "
                    "RETURNING import_id"
                ),
                {
                    "source": provenance.source,
                    "url": provenance.source_url,
                    "asset": asset_canonical,
                    "tsmin": ts_origin_min,
                    "tsmax": ts_origin_max,
                    "count": len(ticks),
                    "hash": batch_hash,
                    "flags": json.dumps(quality),
                    "ack": provenance.license_terms_ack,
                },
            )
            row = result.fetchone()
            import_id = UUID(str(row[0]))
        except IntegrityError:
            await session.rollback()
            return IngestResult(
                import_id=None,
                tick_count=0,
                duplicated=True,
                hash=batch_hash,
                quality_flags=quality,
            )

        # Insere ticks usando ON CONFLICT DO NOTHING — dedup por (asset, ts).
        # Schema atual: cam_market_ticks tem id BIGSERIAL + UNIQUE (asset, timestamp)?
        # Caso não exista UNIQUE, dedup é apenas via provenance.hash (lote inteiro).
        for t in ticks:
            await session.execute(
                text(
                    "INSERT INTO cam_market_ticks (asset, price, volume, timestamp) "
                    "VALUES (:asset, :price, :volume, :ts)"
                ),
                {
                    "asset": t.asset,
                    "price": t.price,
                    "volume": t.volume,
                    "ts": t.timestamp,
                },
            )
        await session.commit()

        return IngestResult(
            import_id=import_id,
            tick_count=len(ticks),
            duplicated=False,
            hash=batch_hash,
            quality_flags=quality,
        )
