from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest, start_http_server

WORKER_READY = Gauge("worker_ready", "Whether the worker is ready to receive work", ["worker"])
WORKER_STARTED = Counter("worker_starts_total", "Number of worker starts", ["worker"])
WORKER_SHUTDOWNS = Counter("worker_shutdowns_total", "Number of graceful worker shutdowns", ["worker"])


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def start_metrics_server(port: int, worker_name: str) -> None:
    WORKER_STARTED.labels(worker=worker_name).inc()
    WORKER_READY.labels(worker=worker_name).set(0)
    start_http_server(port)


@dataclass
class HealthServer:
    port: int
    worker_name: str
    ready_event: asyncio.Event
    shutdown_event: asyncio.Event

    async def start(self) -> web.AppRunner:
        app = web.Application()
        app.router.add_get("/livez", self.livez)
        app.router.add_get("/readyz", self.readyz)
        app.router.add_get("/metrics", self.metrics)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        return runner

    async def livez(self, _request: web.Request) -> web.Response:
        if self.shutdown_event.is_set():
            return web.Response(status=503, text="shutting down\n")
        return web.Response(text="ok\n")

    async def readyz(self, _request: web.Request) -> web.Response:
        if self.ready_event.is_set() and not self.shutdown_event.is_set():
            return web.Response(text="ready\n")
        return web.Response(status=503, text="not ready\n")

    async def metrics(self, _request: web.Request) -> web.Response:
        return web.Response(body=generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})
