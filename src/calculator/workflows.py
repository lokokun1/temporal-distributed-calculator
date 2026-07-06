from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from calculator.parser import BinaryNode, ExpressionNode, NumberNode, Operator, UnaryNode, parse_expression
    from calculator.task_queues import OPERATOR_ACTIVITY_NAMES, OPERATOR_TASK_QUEUES


@workflow.defn
class CalculatorWorkflow:
    @workflow.run
    async def run(self, expression: str) -> float:
        ast = parse_expression(expression)
        return await self._evaluate(ast)

    async def _evaluate(self, node: ExpressionNode) -> float:
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, UnaryNode):
            value = await self._evaluate(node.operand)
            if node.operator is Operator.SUBTRACT:
                return await self._execute_operator(Operator.SUBTRACT, 0, value)
            raise ValueError(f"Unsupported unary operator {node.operator}")

        if isinstance(node, BinaryNode):
            left = await self._evaluate(node.left)
            right = await self._evaluate(node.right)
            return await self._execute_operator(node.operator, left, right)

        raise TypeError(f"Unsupported expression node {node!r}")

    async def _execute_operator(self, operator: Operator, left: float, right: float) -> float:
        return await workflow.execute_activity(
            OPERATOR_ACTIVITY_NAMES[operator],
            args=[left, right],
            task_queue=OPERATOR_TASK_QUEUES[operator],
            schedule_to_close_timeout=timedelta(seconds=30),
            start_to_close_timeout=timedelta(seconds=10),
        )
