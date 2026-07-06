#!/usr/bin/env bash
set -euo pipefail

JOB_NAME="calc-stress-$(date +%s)"
WAVES="${WAVES:-5}"
MAX_BATCH="${MAX_BATCH:-50}"
SLEEP_SECONDS="${SLEEP_SECONDS:-10}"

cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ${JOB_NAME}
  namespace: temporal-calc
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: stress
          image: temporal-distributed-calculator:local
          imagePullPolicy: IfNotPresent
          command: ["/usr/local/bin/python", "-m", "calculator.stress"]
          args:
            - "--waves"
            - "${WAVES}"
            - "--max-batch"
            - "${MAX_BATCH}"
            - "--sleep-seconds"
            - "${SLEEP_SECONDS}"
          env:
            - name: TEMPORAL_ADDRESS
              value: temporal.temporal-calc.svc.cluster.local:7233
EOF

echo "watch load with:"
echo "  kubectl -n temporal-calc get hpa -w"
echo "  kubectl -n temporal-calc get pods -w"
kubectl -n temporal-calc logs -f "job/$JOB_NAME"
