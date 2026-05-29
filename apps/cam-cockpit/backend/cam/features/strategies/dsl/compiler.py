"""
DSL Compiler — TASK-061 (BL-I SPEC v0.4).

Compila DSLAst → classe `Strategy` válida em runtime.

⚠️ SEC: usa AST controlado + sem `eval/exec` arbitrário.
   Expressões de entrada são parseadas com ast.parse(mode='eval') e
   passam por whitelist de nomes/operadores antes de compilarem.
"""
from __future__ import annotations

import ast
import hashlib
from decimal import Decimal
from typing import Any

from cam._shared.domain.primitives import AssetType, ContractCount, Direction
from cam._shared.risk.context import OrderCandidate
from cam.features.strategies.domain import (
    StrategyContext,
    StrategyMetadata,
)
from cam.features.strategies.dsl.parser import DSLAst


class UnsafeExpressionError(ValueError):
    """Expressão DSL contém construções não permitidas."""


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or, ast.Not,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
    ast.UnaryOp, ast.USub, ast.UAdd,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Constant, ast.Name, ast.Attribute, ast.Load,
)


def _validate_expression(expr: str) -> ast.Expression:
    """Parseia expressão e verifica que só usa nodes permitidos."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as err:
        raise UnsafeExpressionError(f"Sintaxe inválida: {expr!r}") from err
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise UnsafeExpressionError(
                f"Construção proibida em expressão DSL: {type(node).__name__}"
            )
    return tree


def _eval_safe(expr_code, env: dict[str, Any]) -> Any:
    """Compila + roda. Já validado por _validate_expression."""
    return eval(expr_code, {"__builtins__": {}}, env)  # noqa: S307


def compile_strategy(ast_obj: DSLAst):
    """
    Retorna classe `Strategy` (não instância) compilada a partir do AST.

    A classe instanciada é registrável no `StrategyRegistry` com
    `compiled_from_dsl=True` em `metadata.custom_metrics`.
    """
    # Validação de expressions
    long_expr = ast_obj.entry.long_condition
    short_expr = ast_obj.entry.short_condition
    long_compiled = None
    short_compiled = None
    if long_expr:
        long_tree = _validate_expression(long_expr)
        long_compiled = compile(long_tree, "<dsl_long>", "eval")
    if short_expr:
        short_tree = _validate_expression(short_expr)
        short_compiled = compile(short_tree, "<dsl_short>", "eval")

    asset_enum = AssetType(ast_obj.asset)
    name = ast_obj.strategy_name
    sl_points = ast_obj.exit.stop_loss or 150
    indicators = ast_obj.indicators

    # Compute deterministic UUID v5 from name+version+asset
    digest = hashlib.sha256(
        f"{name}|1.0.0|{asset_enum.value}".encode()
    ).digest()
    # UUID v4-like (16 bytes from digest, no version bits — placeholder).
    from uuid import UUID

    sid = UUID(bytes=digest[:16])

    class _Compiled:
        metadata = StrategyMetadata(
            id=sid,
            name=name,
            version="1.0.0",
            asset=asset_enum,
            author="dsl",
            custom_metrics={
                "compiled_from_dsl": True,
                "indicators": [
                    {"type": i.type, "params": i.params} for i in indicators
                ],
            },
        )

        def evaluate(
            self, tick: dict[str, Any], context: StrategyContext
        ) -> OrderCandidate | None:
            env = {
                "price": float(tick.get("price", 0)),
                "high": float(tick.get("high", tick.get("price", 0))),
                "low": float(tick.get("low", tick.get("price", 0))),
            }
            if long_compiled is not None and _eval_safe(long_compiled, env):
                return OrderCandidate(
                    asset=asset_enum,
                    direction=Direction.LONG,
                    contracts=ContractCount(1),
                    intended_stop_loss_points=Decimal(str(sl_points)),
                )
            if short_compiled is not None and _eval_safe(short_compiled, env):
                return OrderCandidate(
                    asset=asset_enum,
                    direction=Direction.SHORT,
                    contracts=ContractCount(1),
                    intended_stop_loss_points=Decimal(str(sl_points)),
                )
            return None

    _Compiled.__qualname__ = f"DSL_{name.replace(' ', '_')}"
    _Compiled.__name__ = f"DSL_{name.replace(' ', '_')}"
    return _Compiled
