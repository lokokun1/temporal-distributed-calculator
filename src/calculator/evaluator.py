from __future__ import annotations

from calculator.parser import BinaryNode, ExpressionNode, NumberNode, Operator, UnaryNode


def evaluate_locally(node: ExpressionNode) -> float:
    if isinstance(node, NumberNode):
        return node.value
    if isinstance(node, UnaryNode):
        value = evaluate_locally(node.operand)
        if node.operator is Operator.SUBTRACT:
            return -value
        raise ValueError(f"Unsupported unary operator {node.operator}")
    if isinstance(node, BinaryNode):
        left = evaluate_locally(node.left)
        right = evaluate_locally(node.right)
        return apply_operator(node.operator, left, right)
    raise TypeError(f"Unsupported node {node!r}")


def apply_operator(operator: Operator, left: float, right: float) -> float:
    match operator:
        case Operator.ADD:
            return left + right
        case Operator.SUBTRACT:
            return left - right
        case Operator.MULTIPLY:
            return left * right
        case Operator.DIVIDE:
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return left / right
        case Operator.POWER:
            return left**right
    raise ValueError(f"Unsupported operator {operator}")
