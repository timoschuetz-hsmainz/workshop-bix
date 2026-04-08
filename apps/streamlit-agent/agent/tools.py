from __future__ import annotations

import ast
import operator
from typing import Any

from langchain_core.tools import tool


ALLOWED_OPERATORS: dict[type[ast.AST], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def _compute_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _compute_node(node.left)
        right = _compute_node(node.right)
        return float(ALLOWED_OPERATORS[type(node.op)](left, right))

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_compute_node(node.operand)

    raise ValueError("Only basic numeric expressions are allowed.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the result."""
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _compute_node(parsed.body)
        if result.is_integer():
            return str(int(result))
        return str(result)
    except Exception as exc:  # noqa: BLE001
        return f"calculator_error: {exc}"


TOOLS = [calculator]
