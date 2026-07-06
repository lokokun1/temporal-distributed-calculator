#!/usr/bin/env bash
set -euo pipefail

EXPRESSION="${1:-1 + 5^3 * (2 - 5)}"
JOB_NAME="calc-trigger-$(date +%s)"

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
        - name: trigger
          image: temporal-distributed-calculator:local
          imagePullPolicy: IfNotPresent
          command: ["/usr/local/bin/python", "-m", "calculator.client"]
          args: ["${EXPRESSION}"]
          env:
            - name: TEMPORAL_ADDRESS
              value: temporal.temporal-calc.svc.cluster.local:7233
EOF

kubectl -n temporal-calc wait --for=condition=complete "job/$JOB_NAME" --timeout=120s
kubectl -n temporal-calc logs "job/$JOB_NAME"
