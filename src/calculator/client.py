from __future__ import annotations

import argparse
import asyncio
import os
import uuid

from temporalio.client import Client

from calculator.task_queues import WORKFLOW_TASK_QUEUE
from calculator.workflows import CalculatorWorkflow


async def run_calculation(expression: str) -> float:
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    client = await Client.connect(temporal_address, namespace=namespace)
    return await client.execute_workflow(
        CalculatorWorkflow.run,
        expression,
        id=f"calculator-{uuid.uuid4()}",
        task_queue=os.getenv("WORKFLOW_TASK_QUEUE", WORKFLOW_TASK_QUEUE),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Trigger a distributed calculator workflow.")
    parser.add_argument("expression", help="Arithmetic expression to evaluate")
    args = parser.parse_args()
    result = asyncio.run(run_calculation(args.expression))
    print(f"expression = {args.expression}")
    print(f"result = {result:g}")


if __name__ == "__main__":
    main()
