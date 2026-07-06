from __future__ import annotations

import argparse
import asyncio
import os
import random
import uuid

from temporalio.client import Client

from calculator.task_queues import WORKFLOW_TASK_QUEUE
from calculator.workflows import CalculatorWorkflow

EXPRESSIONS = [
    "1 + 5^3 * (2 - 5)",
    "((10 + 2) * 3 - 4) / 2",
    "2^8 + 100 / (3 + 2)",
    "-3 + 4 * (8 - 2^2)",
    "(7 - 2) ^ 3 / 5 + 11",
]


async def submit_batch(client: Client, count: int) -> None:
    handles = []
    for _ in range(count):
        expression = random.choice(EXPRESSIONS)
        handles.append(
            await client.start_workflow(
                CalculatorWorkflow.run,
                expression,
                id=f"stress-calculator-{uuid.uuid4()}",
                task_queue=os.getenv("WORKFLOW_TASK_QUEUE", WORKFLOW_TASK_QUEUE),
            )
        )
    results = await asyncio.gather(*(handle.result() for handle in handles))
    print(f"completed {len(results)} workflows")


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Create rising and falling calculator load.")
    parser.add_argument("--waves", type=int, default=5)
    parser.add_argument("--max-batch", type=int, default=50)
    parser.add_argument("--sleep-seconds", type=float, default=10)
    args = parser.parse_args()

    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )
    batch_sizes = list(range(5, args.max_batch + 1, max(1, args.max_batch // args.waves)))
    batch_sizes += list(reversed(batch_sizes))
    for batch_size in batch_sizes:
        print(f"submitting batch_size={batch_size}")
        await submit_batch(client, batch_size)
        await asyncio.sleep(args.sleep_seconds)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
