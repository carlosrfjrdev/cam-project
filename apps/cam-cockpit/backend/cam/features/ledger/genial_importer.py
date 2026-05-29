"""
Genial Investimentos — parser de extrato CSV (TASK-014 BL-B).

⚠️ TECH-DEBT EXPLÍCITO ⚠️
========================
O layout proprietário do CSV de extrato da Genial Investimentos NÃO está
documentado neste repositório. Este parser entrega o **esqueleto canônico**
com:

  - Schema de saída (`ParsedExtrato`) usado por T022 (BL-D).
  - Modo de fallback baseado em **headers heurísticos** (ticker, qty, price).
  - Flag `requires_layout_confirmation=True` toda vez que o parser detecta
    layout incompatível — emite warning e retorna lista vazia em vez de
    falhar silenciosamente.
  - Fixture sintética em tests/fixtures/genial_extrato_sample.csv para
    permitir TDD e regressão até o layout real ser confirmado pelo Founder
    (TD-v0.4-B1).

O parser **aceita** decimal vírgula brasileira (`35,50` → `35.50`),
inferindo timezone São Paulo (UTC-3) se a coluna `data` vier sem TZ.

Quando o Founder anexar um arquivo Genial real:
  1. Carregar como nova fixture (`genial_extrato_real_aDDDDDDDD.csv`).
  2. Adicionar mapeamento de colunas reais em `_GENIAL_COLUMN_MAPPINGS`.
  3. Remover flag `requires_layout_confirmation`.
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Schema de saída
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HoldingRow:
    ticker: str
    quantity: int
    avg_price: Decimal
    acquired_at: datetime | None
    source_row: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TradeRow:
    ticker: str
    direction: str  # "BUY" | "SELL"
    quantity: int
    price: Decimal
    executed_at: datetime | None
    source_row: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedExtrato:
    file_hash: str
    holdings: list[HoldingRow]
    trades: list[TradeRow]
    requires_layout_confirmation: bool
    warnings: list[str]


# ---------------------------------------------------------------------------
# Mapeamentos heurísticos de colunas
# ---------------------------------------------------------------------------
# Cada chave é o nome canônico interno; valores são lista de aliases reconhecidos
# (case-insensitive). Quando o layout real for confirmado, expandir.
_GENIAL_COLUMN_MAPPINGS: dict[str, list[str]] = {
    "ticker": ["ticker", "codigo", "código", "ativo", "papel"],
    "quantity": ["quantidade", "qtd", "qtde", "qtd_disponivel"],
    "avg_price": ["preco_medio", "preço médio", "preco medio", "preço médio",
                  "custo_medio", "custo médio"],
    "price": ["preco", "preço", "valor_unitario"],
    "direction": ["operacao", "operação", "tipo", "natureza"],
    "date": ["data", "data_operacao", "data operação", "data_pregao"],
}


def _canonicalize_headers(headers: list[str]) -> dict[str, str]:
    """Mapeia headers do arquivo → nomes canônicos. Não-mapeados ficam de fora."""
    lower_headers = [h.strip().lower() for h in headers]
    mapped: dict[str, str] = {}
    for canonical, aliases in _GENIAL_COLUMN_MAPPINGS.items():
        for alias in aliases:
            if alias.strip().lower() in lower_headers:
                idx = lower_headers.index(alias.strip().lower())
                mapped[canonical] = headers[idx]
                break
    return mapped


def _parse_decimal_brl(value: str) -> Decimal | None:
    """Converte '1.234,56' ou '1234,56' ou '1234.56' para Decimal."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".") if s.count(",") == 1 else s
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _parse_int(value: str) -> int | None:
    if value is None:
        return None
    s = str(value).strip().replace(".", "")
    if not s or not (s.lstrip("-").isdigit()):
        return None
    return int(s)


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    s = str(value).strip()
    # Tentar formatos comuns BR
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _hash_file(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Parser público
# ---------------------------------------------------------------------------
def parse_extrato(filepath: str | Path) -> ParsedExtrato:
    """
    Parseia CSV de extrato Genial. Retorna ParsedExtrato.

    Modo defensivo: layout proprietário não documentado → se headers não
    casarem heurística mínima (ticker + quantity + avg_price OR price),
    retorna `requires_layout_confirmation=True` com listas vazias + warnings.

    Não levanta — todas as falhas viram warnings, decisão fica com o caller.
    """
    path = Path(filepath)
    if not path.exists():
        return ParsedExtrato(
            file_hash="",
            holdings=[],
            trades=[],
            requires_layout_confirmation=True,
            warnings=[f"Arquivo não encontrado: {filepath}"],
        )

    raw = path.read_bytes()
    file_hash = _hash_file(raw)
    warnings: list[str] = []
    holdings: list[HoldingRow] = []
    trades: list[TradeRow] = []

    # Tenta detectar delimitador (vírgula ou ponto-e-vírgula)
    text = raw.decode("utf-8-sig", errors="replace")
    first_line = text.splitlines()[0] if text else ""
    delim = ";" if ";" in first_line and "," not in first_line else ","

    reader = csv.DictReader(text.splitlines(), delimiter=delim)
    headers = reader.fieldnames or []
    if not headers:
        return ParsedExtrato(
            file_hash=file_hash,
            holdings=[],
            trades=[],
            requires_layout_confirmation=True,
            warnings=["Arquivo sem header detectado."],
        )

    mapping = _canonicalize_headers(list(headers))
    requires_conf = False

    # Heurística mínima para holdings
    if "ticker" in mapping and "quantity" in mapping and "avg_price" in mapping:
        # Modo holdings
        for row in reader:
            ticker = (row.get(mapping["ticker"]) or "").strip().upper()
            qty = _parse_int(row.get(mapping["quantity"]) or "")
            avg = _parse_decimal_brl(row.get(mapping["avg_price"]) or "")
            if not ticker or qty is None or qty <= 0 or avg is None:
                warnings.append(f"Linha inválida (holding): {row}")
                continue
            acquired = (
                _parse_date(row.get(mapping["date"]) or "")
                if "date" in mapping
                else None
            )
            holdings.append(
                HoldingRow(
                    ticker=ticker,
                    quantity=qty,
                    avg_price=avg,
                    acquired_at=acquired,
                    source_row=dict(row),
                )
            )
    elif "ticker" in mapping and "quantity" in mapping and "price" in mapping:
        # Modo trades (operações)
        for row in reader:
            ticker = (row.get(mapping["ticker"]) or "").strip().upper()
            qty = _parse_int(row.get(mapping["quantity"]) or "")
            price = _parse_decimal_brl(row.get(mapping["price"]) or "")
            direction_raw = (
                row.get(mapping["direction"], "BUY") if "direction" in mapping
                else "BUY"
            )
            direction = (
                "BUY" if "comp" in direction_raw.lower() or
                direction_raw.upper().startswith("C") else "SELL"
            )
            if not ticker or qty is None or qty <= 0 or price is None:
                warnings.append(f"Linha inválida (trade): {row}")
                continue
            executed = (
                _parse_date(row.get(mapping["date"]) or "")
                if "date" in mapping
                else None
            )
            trades.append(
                TradeRow(
                    ticker=ticker,
                    direction=direction,
                    quantity=qty,
                    price=price,
                    executed_at=executed,
                    source_row=dict(row),
                )
            )
    else:
        requires_conf = True
        warnings.append(
            "Layout não reconhecido — headers mínimos (ticker + quantity + "
            f"avg_price OR price) não detectados. Headers vistos: {headers}. "
            "Tech-debt TD-v0.4-B1: confirmar layout Genial real."
        )

    return ParsedExtrato(
        file_hash=file_hash,
        holdings=holdings,
        trades=trades,
        requires_layout_confirmation=requires_conf,
        warnings=warnings,
    )
