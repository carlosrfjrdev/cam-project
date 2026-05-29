"""
DSL Parser — TASK-060 (BL-I SPEC v0.4).

Lê YAML/JSON declarativo e produz AST `DSLAst` consumido por T061.

Formato canônico (SPEC §13.1):

    strategy: my_orb
    asset: WIN
    indicators:
      - type: opening_range
        minutes: 60
    entry:
      long: "price > opening_range.high"
    exit:
      stop_loss: 150
      take_profit: 300
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class DSLParseError(ValueError):
    """Parse falhou — DSL inválida ou faltam campos obrigatórios."""


_REQUIRED_TOP_LEVEL = {"strategy", "asset", "indicators", "entry", "exit"}
_VALID_INDICATORS = {"opening_range", "ema", "sma", "rsi"}


@dataclass(frozen=True)
class IndicatorSpec:
    type: str
    params: dict[str, Any]


@dataclass(frozen=True)
class EntrySpec:
    long_condition: str | None = None
    short_condition: str | None = None


@dataclass(frozen=True)
class ExitSpec:
    stop_loss: int | None = None
    take_profit: int | str | None = None


@dataclass(frozen=True)
class DSLAst:
    strategy_name: str
    asset: str
    indicators: tuple[IndicatorSpec, ...]
    entry: EntrySpec
    exit: ExitSpec


def parse(source: str | dict | Path) -> DSLAst:
    """
    Parseia DSL (YAML, JSON ou dict). Levanta DSLParseError em qualquer
    inconsistência.
    """
    if isinstance(source, dict):
        data: dict[str, Any] = source
    elif isinstance(source, Path):
        text = source.read_text(encoding="utf-8")
        data = _load_text(text)
    else:
        data = _load_text(source)

    if not isinstance(data, dict):
        raise DSLParseError(f"Root deve ser dict; recebido {type(data)}")

    missing = _REQUIRED_TOP_LEVEL - set(data.keys())
    if missing:
        raise DSLParseError(f"Campos obrigatórios ausentes: {sorted(missing)}")

    indicators_raw = data["indicators"]
    if not isinstance(indicators_raw, list):
        raise DSLParseError("`indicators` deve ser lista")
    indicators = []
    for spec in indicators_raw:
        if not isinstance(spec, dict) or "type" not in spec:
            raise DSLParseError(f"Indicator inválido: {spec}")
        if spec["type"] not in _VALID_INDICATORS:
            raise DSLParseError(
                f"Indicator tipo desconhecido: {spec['type']!r}. "
                f"Suportados: {sorted(_VALID_INDICATORS)}"
            )
        params = {k: v for k, v in spec.items() if k != "type"}
        indicators.append(IndicatorSpec(type=spec["type"], params=params))

    entry_raw = data["entry"]
    if not isinstance(entry_raw, dict):
        raise DSLParseError("`entry` deve ser dict")
    entry = EntrySpec(
        long_condition=entry_raw.get("long"),
        short_condition=entry_raw.get("short"),
    )

    exit_raw = data["exit"]
    if not isinstance(exit_raw, dict):
        raise DSLParseError("`exit` deve ser dict")
    exit_spec = ExitSpec(
        stop_loss=exit_raw.get("stop_loss"),
        take_profit=exit_raw.get("take_profit"),
    )

    return DSLAst(
        strategy_name=str(data["strategy"]),
        asset=str(data["asset"]).upper(),
        indicators=tuple(indicators),
        entry=entry,
        exit=exit_spec,
    )


def _load_text(text: str) -> Any:
    """Tenta JSON, depois YAML."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as err:
            raise DSLParseError(f"YAML inválido: {err}") from err
