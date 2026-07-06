from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Operator(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "^"


@dataclass(frozen=True)
class NumberNode:
    value: float


@dataclass(frozen=True)
class UnaryNode:
    operator: Operator
    operand: "ExpressionNode"


@dataclass(frozen=True)
class BinaryNode:
    operator: Operator
    left: "ExpressionNode"
    right: "ExpressionNode"


ExpressionNode = NumberNode | UnaryNode | BinaryNode


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


class ExpressionSyntaxError(ValueError):
    pass


_PRECEDENCE = {
    Operator.ADD: 10,
    Operator.SUBTRACT: 10,
    Operator.MULTIPLY: 20,
    Operator.DIVIDE: 20,
    Operator.POWER: 30,
}
_RIGHT_ASSOCIATIVE = {Operator.POWER}


def parse_expression(source: str) -> ExpressionNode:
    parser = _Parser(_tokenize(source))
    expression = parser.parse_expression()
    parser.expect("EOF")
    return expression


def _tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char.isdigit() or char == ".":
            start = index
            seen_dot = char == "."
            index += 1
            while index < len(source):
                current = source[index]
                if current == ".":
                    if seen_dot:
                        raise ExpressionSyntaxError(f"Invalid number at position {start}")
                    seen_dot = True
                    index += 1
                    continue
                if not current.isdigit():
                    break
                index += 1
            value = source[start:index]
            if value == ".":
                raise ExpressionSyntaxError(f"Invalid number at position {start}")
            tokens.append(Token("NUMBER", value, start))
            continue
        if char in "+-*/^":
            tokens.append(Token("OPERATOR", char, index))
            index += 1
            continue
        if char == "(":
            tokens.append(Token("LPAREN", char, index))
            index += 1
            continue
        if char == ")":
            tokens.append(Token("RPAREN", char, index))
            index += 1
            continue
        raise ExpressionSyntaxError(f"Unexpected character {char!r} at position {index}")
    tokens.append(Token("EOF", "", len(source)))
    return tokens


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse_expression(self, min_precedence: int = 0) -> ExpressionNode:
        left = self.parse_prefix()

        while self.current.kind == "OPERATOR":
            operator = Operator(self.current.value)
            precedence = _PRECEDENCE[operator]
            if precedence < min_precedence:
                break
            self.advance()
            next_min = precedence if operator in _RIGHT_ASSOCIATIVE else precedence + 1
            right = self.parse_expression(next_min)
            left = BinaryNode(operator=operator, left=left, right=right)

        return left

    def parse_prefix(self) -> ExpressionNode:
        token = self.current
        if token.kind == "NUMBER":
            self.advance()
            return NumberNode(float(token.value))
        if token.kind == "OPERATOR" and token.value in "+-":
            self.advance()
            operand = self.parse_expression(_PRECEDENCE[Operator.POWER])
            if token.value == "+":
                return operand
            return UnaryNode(operator=Operator.SUBTRACT, operand=operand)
        if token.kind == "LPAREN":
            self.advance()
            expression = self.parse_expression()
            self.expect("RPAREN")
            return expression
        raise ExpressionSyntaxError(f"Expected number or '(' at position {token.position}")

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def expect(self, kind: str) -> Token:
        token = self.current
        if token.kind != kind:
            expected = "end of expression" if kind == "EOF" else kind
            raise ExpressionSyntaxError(f"Expected {expected} at position {token.position}")
        return self.advance()
