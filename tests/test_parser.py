from __future__ import annotations

import pytest

from calculator.evaluator import evaluate_locally
from calculator.parser import BinaryNode, ExpressionSyntaxError, Operator, parse_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 + 5^3 * (2 - 5)", -374),
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("2^3^2", 512),
        ("10 - 3 - 2", 5),
        ("-3^2", -9),
        ("(-3)^2", 9),
        ("3.5 * 2", 7),
    ],
)
def test_expression_evaluation(expression: str, expected: float) -> None:
    assert evaluate_locally(parse_expression(expression)) == expected


def test_power_is_right_associative() -> None:
    ast = parse_expression("2^3^2")
    assert isinstance(ast, BinaryNode)
    assert ast.operator is Operator.POWER
    assert isinstance(ast.right, BinaryNode)
    assert ast.right.operator is Operator.POWER


@pytest.mark.parametrize("expression", ["", "1 +", "1..2", "1 + )", "(1 + 2"])
def test_invalid_expressions_raise(expression: str) -> None:
    with pytest.raises(ExpressionSyntaxError):
        parse_expression(expression)
