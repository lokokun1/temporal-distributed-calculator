# Design

## Goal

The goal is to show a small but realistic platform pattern around Temporal workers:

- shared worker bootstrap
- explicit task queue ownership
- Kubernetes-native health checks
- basic observability
- enough tests to make the expression behavior trustworthy

## Worker SDK

The SDK lives under `src/worker_sdk`.

It standardizes:

- Temporal connection setup
- env-based configuration
- logging setup
- graceful shutdown on `SIGTERM` / `SIGINT`
- liveness and readiness endpoints
- Prometheus metrics

The important design choice is that health and metrics are not implemented inside each worker. A worker only calls:

```python
await run_worker(config=..., workflows=[...], activities=[...])
```

That means an existing worker can receive probes by upgrading the SDK and using the same bootstrap path.

## Calculator Workflow

The workflow receives one string expression. It parses the expression into an AST and evaluates the AST recursively.

Numbers are returned directly. Operator nodes are executed as Temporal activities. Each operator has:

- a distinct activity name
- a distinct task queue
- a distinct worker deployment

This keeps the workflow as the orchestrator and makes the distributed boundary visible.

## Parsing

The parser is a Pratt-style precedence parser. It supports:

- `+`
- `-`
- `*`
- `/`
- `^`
- parentheses
- unary plus and minus
- decimal numbers

Associativity:

- `^` is right-associative, so `2^3^2` is parsed as `2^(3^2)`.
- `+`, `-`, `*`, `/` are left-associative.

This keeps the parser small while still making operator behavior explicit and testable.

## Kubernetes

The Kubernetes setup uses plain manifests instead of Helm.

Tradeoff:

- Manifests are easier to inspect in a home assessment.
- Helm would be better if this were intended as a reusable installable product.

The deployment uses a single application image and changes worker behavior with env vars. This avoids building five almost identical images.

Temporal is deployed as a local dev server for kind. That is not a production Temporal topology, but it is appropriate for a local assessment because the focus is worker orchestration and platform ergonomics.

## Autoscaling

The included HPA scales operator workers on CPU utilization.

Why CPU:

- it works with standard Kubernetes HPA
- it is easy to run in kind
- it does not require installing Prometheus Adapter or KEDA

Limitations:

- CPU is an indirect signal for Temporal queue pressure.
- A worker can have a large backlog while CPU is low, for example if work is blocked on external I/O.
- HPA reacts after load is already visible, so short bursts may finish before scaling helps.

Preferred production metric:

- Temporal task queue schedule-to-start latency
- pending activity task backlog per task queue

Those metrics better describe whether more workers are needed.
