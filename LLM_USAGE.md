# LLM Usage

An LLM was used as a pair-programming assistant for this assessment.

## Prompts

The initial prompt was the full home assessment text:

```text
Build a small Temporal-based distributed system, package it as a reusable worker SDK, and run it locally on Kubernetes.
```

Follow-up prompts focused on:

- choosing Python as the implementation language
- preparing the Windows 11 VM environment
- deciding a practical local Kubernetes setup
- structuring the deliverables
- implementing the project incrementally

## Planning Approach

The work was broken into these steps:

1. Prepare the development environment.
2. Create a Python project skeleton.
3. Implement and test expression parsing.
4. Add Temporal workflow and operator activities.
5. Extract common worker concerns into an SDK.
6. Add Docker and Kubernetes deployment files.
7. Add trigger and stress-test scripts.
8. Write README and design documentation.

## Iterations

Approximate number of iterations: 6.

The iterations were:

- environment setup and dependency choices
- repository structure
- parser and local tests
- Temporal worker/workflow wiring
- Kubernetes manifests and scripts
- documentation and design explanation

## How Iterations Could Be Reduced

The number of iterations could be reduced by deciding these up front:

- whether Temporal should run as a dev server or a full cluster
- whether autoscaling should use CPU HPA or Temporal queue metrics
- whether the deliverable should be Helm-first or manifest-first
- exact target OS and shell for scripts

Those choices affect project structure and local run instructions, so resolving them early would reduce rework.
