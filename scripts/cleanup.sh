#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-temporal-calc}"
kind delete cluster --name "$CLUSTER_NAME"
