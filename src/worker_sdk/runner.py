from __future__ import annotations

import asyncio
import logging
import signal
from collections.abc import Sequence

from temporalio.client import Client
from temporalio.worker import Worker

from worker_sdk.config import WorkerConfig
from worker_sdk.observability import (
    HealthServer,
    WORKER_READY,
    WORKER_SHUTDOWNS,
    configure_logging,
    start_metrics_server,
)

logger = logging.getLogger(__name__)


async def run_worker(
    *,
    config: WorkerConfig,
    workflows: Sequence[type] = (),
    activities: Sequence[object] = (),
) -> None:
    configure_logging(config.log_level)
    shutdown_event = asyncio.Event()
    ready_event = asyncio.Event()
    health_runner = None

    _install_signal_handlers(shutdown_event)

    if config.enable_metrics:
        start_metrics_server(config.metrics_port, config.worker_name)

    if config.enable_health:
        health_runner = await HealthServer(
            port=config.health_port,
            worker_name=config.worker_name,
            ready_event=ready_event,
            shutdown_event=shutdown_event,
        ).start()

    logger.info(
        "connecting to temporal",
        extra={
            "worker": config.worker_name,
            "address": config.temporal_address,
            "namespace": config.namespace,
            "task_queue": config.task_queue,
        },
    )
    client = await Client.connect(config.temporal_address, namespace=config.namespace)
    worker = Worker(
        client,
        task_queue=config.task_queue,
        workflows=list(workflows),
        activities=list(activities),
        max_concurrent_activities=config.max_concurrent_activities,
    )

    ready_event.set()
    WORKER_READY.labels(worker=config.worker_name).set(1)
    logger.info("worker started", extra={"worker": config.worker_name})

    worker_task = asyncio.create_task(worker.run())
    shutdown_task = asyncio.create_task(shutdown_event.wait())
    done, pending = await asyncio.wait(
        {worker_task, shutdown_task},
        return_when=asyncio.FIRST_COMPLETED,
    )

    if shutdown_task in done:
        logger.info("shutdown requested", extra={"worker": config.worker_name})
        ready_event.clear()
        WORKER_READY.labels(worker=config.worker_name).set(0)
        worker_task.cancel()

    for task in pending:
        task.cancel()

    await asyncio.gather(worker_task, shutdown_task, return_exceptions=True)
    WORKER_SHUTDOWNS.labels(worker=config.worker_name).inc()

    if health_runner:
        await health_runner.cleanup()

    logger.info("worker stopped", extra={"worker": config.worker_name})


def _install_signal_handlers(shutdown_event: asyncio.Event) -> None:
    def request_shutdown(_signum: int, _frame: object) -> None:
        shutdown_event.set()

    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)
