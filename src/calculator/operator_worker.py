from __future__ import annotations

import asyncio
import os

from calculator import activities
from calculator.parser import Operator
from calculator.task_queues import OPERATOR_TASK_QUEUES
from worker_sdk import WorkerConfig, run_worker

_ACTIVITIES = {
    Operator.ADD: activities.add,
    Operator.SUBTRACT: activities.subtract,
    Operator.MULTIPLY: activities.multiply,
    Operator.DIVIDE: activities.divide,
    Operator.POWER: activities.power,
}


def _operator_from_env() -> Operator:
    raw = os.getenv("OPERATOR")
    if not raw:
        raise ValueError("OPERATOR must be set to one of: +, -, *, /, ^")
    try:
        return Operator(raw)
    except ValueError as exc:
        raise ValueError("OPERATOR must be one of: +, -, *, /, ^") from exc


async def main_async() -> None:
    operator = _operator_from_env()
    await run_worker(
        config=WorkerConfig.from_env(
            default_task_queue=OPERATOR_TASK_QUEUES[operator],
            default_worker_name=f"operator-{operator.value}",
        ),
        activities=[_ACTIVITIES[operator]],
    )


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
