
#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-temporal-calc}"
IMAGE="${IMAGE:-temporal-distributed-calculator:local}"
TEMPORAL_IMAGE="${TEMPORAL_IMAGE:-temporalio/admin-tools:latest}"

docker build -t "$IMAGE" .
kind load docker-image "$IMAGE" --name "$CLUSTER_NAME"

docker pull "$TEMPORAL_IMAGE"

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/temporal-dev-server.yaml
kubectl apply -f k8s/workflow-worker.yaml
kubectl apply -f k8s/operator-workers.yaml

kubectl -n temporal-calc rollout status deploy/temporal --timeout=180s
kubectl -n temporal-calc rollout status deploy/workflow-worker --timeout=180s
kubectl -n temporal-calc rollout status deploy/add-worker --timeout=180s
kubectl -n temporal-calc rollout status deploy/subtract-worker --timeout=180s
kubectl -n temporal-calc rollout status deploy/multiply-worker --timeout=180s
kubectl -n temporal-calc rollout status deploy/divide-worker --timeout=180s
kubectl -n temporal-calc rollout status deploy/power-worker --timeout=180s

echo "deployment complete"
