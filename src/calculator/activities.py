from __future__ import annotations

import asyncio
import logging
import os

from prometheus_client import Counter
from temporalio import activity

logger = logging.getLogger(__name__)
ACTIVITY_EXECUTIONS = Counter(
    "calculator_activity_executions_total",
    "Number of calculator operator activity executions",
    ["operator"],
)


async def _optional_delay() -> None:
    delay_ms = int(os.getenv("ACTIVITY_DELAY_MS", "0"))
    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000)


@activity.defn(name="calculator.add")
async def add(left: float, right: float) -> float:
    ACTIVITY_EXECUTIONS.labels(operator="add").inc()
    logger.info("executing add", extra={"left": left, "right": right})
    await _optional_delay()
    return left + right


@activity.defn(name="calculator.subtract")
async def subtract(left: float, right: float) -> float:
    ACTIVITY_EXECUTIONS.labels(operator="subtract").inc()
    logger.info("executing subtract", extra={"left": left, "right": right})
    await _optional_delay()
    return left - right


@activity.defn(name="calculator.multiply")
async def multiply(left: float, right: float) -> float:
    ACTIVITY_EXECUTIONS.labels(operator="multiply").inc()
    logger.info("executing multiply", extra={"left": left, "right": right})
    await _optional_delay()
    return left * right


@activity.defn(name="calculator.divide")
async def divide(left: float, right: float) -> float:
    ACTIVITY_EXECUTIONS.labels(operator="divide").inc()
    logger.info("executing divide", extra={"left": left, "right": right})
    await _optional_delay()
    if right == 0:
        raise ZeroDivisionError("division by zero")
    return left / right


@activity.defn(name="calculator.power")
async def power(left: float, right: float) -> float:
    ACTIVITY_EXECUTIONS.labels(operator="power").inc()
    logger.info("executing power", extra={"left": left, "right": right})
    await _optional_delay()
    return left**right
