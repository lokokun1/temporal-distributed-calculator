from __future__ import annotations

import asyncio

from calculator.task_queues import WORKFLOW_TASK_QUEUE
from calculator.workflows import CalculatorWorkflow
from worker_sdk import WorkerConfig, run_worker


async def main_async() -> None:
    await run_worker(
        config=WorkerConfig.from_env(
            default_task_queue=WORKFLOW_TASK_QUEUE,
            default_worker_name="calculator-workflow-worker",
        ),
        workflows=[CalculatorWorkflow],
    )


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
