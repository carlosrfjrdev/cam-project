"""TDD First — TASK-060 + T061 (BL-I DSL)."""
from __future__ import annotations

import pytest

from cam._shared.domain.primitives import AssetType, Direction
from cam._shared.risk.context import OrderCandidate
from cam.features.strategies.domain import Strategy, StrategyContext
from cam.features.strategies.dsl.compiler import (
    UnsafeExpressionError,
    compile_strategy,
)
from cam.features.strategies.dsl.parser import (
    DSLParseError,
    parse,
)

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
SAMPLE_YAML = """
strategy: my_orb
asset: WIN
indicators:
  - type: opening_range
    minutes: 60
entry:
  long: "price > 130000"
exit:
  stop_loss: 150
  take_profit: 300
"""


class TestParser:
    def test_parses_yaml_with_required_fields(self):
        ast = parse(SAMPLE_YAML)
        assert ast.strategy_name == "my_orb"
        assert ast.asset == "WIN"
        assert len(ast.indicators) == 1
        assert ast.indicators[0].type == "opening_range"
        assert ast.entry.long_condition == "price > 130000"
        assert ast.exit.stop_loss == 150

    def test_parses_dict_directly(self):
        ast = parse({
            "strategy": "s1",
            "asset": "WDO",
            "indicators": [{"type": "ema", "period": 10}],
            "entry": {"short": "price < 5500"},
            "exit": {"stop_loss": 100},
        })
        assert ast.strategy_name == "s1"
        assert ast.asset == "WDO"

    def test_missing_required_field_raises(self):
        with pytest.raises(DSLParseError):
            parse({"strategy": "x", "asset": "WIN", "indicators": []})

    def test_unknown_indicator_type_raises(self):
        with pytest.raises(DSLParseError):
            parse({
                "strategy": "x",
                "asset": "WIN",
                "indicators": [{"type": "nonexistent"}],
                "entry": {},
                "exit": {},
            })

    def test_indicators_must_be_list(self):
        with pytest.raises(DSLParseError):
            parse({
                "strategy": "x",
                "asset": "WIN",
                "indicators": {},  # invalido
                "entry": {},
                "exit": {},
            })


# ---------------------------------------------------------------------------
# Compiler
# ---------------------------------------------------------------------------
class TestCompiler:
    def test_compile_produces_class_with_metadata(self):
        ast = parse(SAMPLE_YAML)
        cls = compile_strategy(ast)
        instance = cls()
        assert isinstance(instance, Strategy)
        assert instance.metadata.asset is AssetType.WIN
        assert instance.metadata.custom_metrics["compiled_from_dsl"] is True

    def test_compiled_strategy_triggers_long_on_match(self):
        ast = parse(SAMPLE_YAML)
        cls = compile_strategy(ast)
        instance = cls()
        result = instance.evaluate(
            {"price": 130100}, StrategyContext(tick={"price": 130100})
        )
        assert isinstance(result, OrderCandidate)
        assert result.direction is Direction.LONG

    def test_compiled_strategy_returns_none_when_no_match(self):
        ast = parse(SAMPLE_YAML)
        cls = compile_strategy(ast)
        instance = cls()
        result = instance.evaluate(
            {"price": 129000}, StrategyContext(tick={"price": 129000})
        )
        assert result is None

    def test_compile_rejects_unsafe_expression(self):
        ast = parse({
            "strategy": "evil",
            "asset": "WIN",
            "indicators": [{"type": "ema", "period": 5}],
            "entry": {"long": "__import__('os').system('echo hack')"},
            "exit": {"stop_loss": 100},
        })
        with pytest.raises(UnsafeExpressionError):
            compile_strategy(ast)

    def test_compile_is_deterministic_id_for_same_ast(self):
        ast_a = parse(SAMPLE_YAML)
        ast_b = parse(SAMPLE_YAML)
        cls_a = compile_strategy(ast_a)
        cls_b = compile_strategy(ast_b)
        assert cls_a().metadata.id == cls_b().metadata.id
