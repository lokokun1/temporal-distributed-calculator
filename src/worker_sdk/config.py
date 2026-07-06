from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerConfig:
    temporal_address: str
    namespace: str
    task_queue: str
    worker_name: str
    health_port: int
    metrics_port: int
    enable_health: bool
    enable_metrics: bool
    log_level: str
    max_concurrent_activities: int

    @classmethod
    def from_env(cls, *, default_task_queue: str, default_worker_name: str) -> "WorkerConfig":
        return cls(
            temporal_address=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
            namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
            task_queue=os.getenv("TASK_QUEUE", default_task_queue),
            worker_name=os.getenv("WORKER_NAME", default_worker_name),
            health_port=int(os.getenv("HEALTH_PORT", "8080")),
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            enable_health=os.getenv("ENABLE_HEALTH", "true").lower() == "true",
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_concurrent_activities=int(os.getenv("MAX_CONCURRENT_ACTIVITIES", "100")),
        )
