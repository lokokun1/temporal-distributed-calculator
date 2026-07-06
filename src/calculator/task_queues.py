from __future__ import annotations

from calculator.parser import Operator

WORKFLOW_TASK_QUEUE = "calculator-workflows"

OPERATOR_TASK_QUEUES = {
    Operator.ADD: "calculator-add",
    Operator.SUBTRACT: "calculator-subtract",
    Operator.MULTIPLY: "calculator-multiply",
    Operator.DIVIDE: "calculator-divide",
    Operator.POWER: "calculator-power",
}

OPERATOR_ACTIVITY_NAMES = {
    Operator.ADD: "calculator.add",
    Operator.SUBTRACT: "calculator.subtract",
    Operator.MULTIPLY: "calculator.multiply",
    Operator.DIVIDE: "calculator.divide",
    Operator.POWER: "calculator.power",
}
