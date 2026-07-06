# Temporal Distributed Calculator

This project is a small Temporal-based distributed system packaged around a reusable Python worker SDK.

It evaluates arithmetic expressions such as:

```text
1 + 5^3 * (2 - 5)
```

The workflow parses the expression, respects precedence and associativity, and delegates each operator type to a separate Temporal task queue handled by a separate worker deployment.

## Requirements

- Python 3.12
- Docker Desktop
- kind
- kubectl
- Optional: Helm, not required by this implementation

## Architecture

- `worker_sdk`: reusable worker bootstrap with env-based config, structured logs, graceful shutdown, metrics, readiness, and liveness probes.
- `calculator.workflow_worker`: hosts the Temporal workflow.
- `calculator.operator_worker`: generic operator worker. The operator is selected by `OPERATOR`.
- Task queues:
  - `calculator-add`
  - `calculator-subtract`
  - `calculator-multiply`
  - `calculator-divide`
  - `calculator-power`
  - `calculator-workflows`

The same container image is reused for all workers. Kubernetes changes the behavior through environment variables.

## Local Python Checks

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[dev]"
pytest
```

## Run on kind

Create a local cluster:

```bash
bash scripts/create-kind-cluster.sh
```

Build the image, load it into kind, and deploy Temporal plus all workers:

```bash
bash scripts/deploy.sh
```

Trigger a calculation:

```bash
bash scripts/trigger-calculation.sh "1 + 5^3 * (2 - 5)"
```

Expected output:

```text
expression = 1 + 5^3 * (2 - 5)
result = -374
```

Check the system:

```bash
kubectl get pods -n temporal-calc
kubectl logs -n temporal-calc deploy/add-worker
kubectl port-forward -n temporal-calc svc/temporal 8233:8233
```

The Temporal UI is then available at `http://localhost:8233`.

## Health and Metrics

Every worker exposes, through the SDK:

- `GET /livez`
- `GET /readyz`
- `GET /metrics`

Kubernetes probes are defined in the manifests. Existing workers only need to upgrade the SDK and keep using `run_worker`; no worker-specific health code is required.

## Autoscaling Bonus

Apply HPAs:

```bash
bash scripts/enable-autoscaling.sh
```

Run a stress test:

```bash
bash scripts/stress-test.sh
```

Watch scaling:

```bash
kubectl get hpa -n temporal-calc -w
kubectl get pods -n temporal-calc -w
```

This implementation uses CPU utilization because it is simple to run locally with the Kubernetes metrics API. In production, I would prefer scaling on Temporal task queue pressure, such as schedule-to-start latency or backlog, exposed through Temporal metrics and consumed by KEDA or a Prometheus Adapter.

## Cleanup

```bash
bash scripts/cleanup.sh
```
