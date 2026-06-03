"""
Snapshot imutável + hash composto — SPEC v0.5 R-16.

Reprodutibilidade: o hash identifica univocamente o dataset (raw ⊕ calendário ⊕
Σ_TF(regra ⊕ definição de barra)). Mudar qualquer regra muda o hash → nova run
vinculada, nunca edita a anterior. Função pura.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def composite_hash(
    raw_canonical_hash: str,
    calendar_version: str,
    timeframes: list[str],
    aggregation_rule_hash: str,
    continuous_series_version: str = "",
) -> str:
    """
    Hash composto determinístico (R-16). Ordena os campos para ser estável.
    """
    payload: dict[str, Any] = {
        "raw": raw_canonical_hash,
        "calendar": calendar_version,
        "timeframes": sorted(timeframes),
        "agg_rule": aggregation_rule_hash,
        "continuous": continuous_series_version,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def batch_hash(rows: list[dict[str, Any]]) -> str:
    """Hash de um lote bruto ingerido (provenance R-03). Determinístico."""
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
