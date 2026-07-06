#!/usr/bin/env bash
set -euo pipefail

echo "Applying HPAs. A metrics-server installation is required for CPU-based scaling."
kubectl apply -f k8s/hpa.yaml
kubectl -n temporal-calc get hpa
