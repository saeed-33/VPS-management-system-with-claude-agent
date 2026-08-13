# Linux Random Runtime Scenarios

## Goal

The scripts under `tools/linux_scenarios/` create bounded, reproducible workloads on disposable Linux test servers so the monitoring and autonomous-diagnosis pipeline can be exercised against conditions that look more like real operations.

They intentionally do **not** change system configuration or perform remediation.

## Available scenarios

The target-side workload generator supports:

```text
cpu
memory
disk-io
process-churn
tcp-listener
http-local
mixed
random
```

All scenarios are designed to run as an unprivileged user.

### CPU

Creates bounded CPU activity with one or more worker processes.

### Memory

Allocates and touches a bounded byte array, then releases it.

### Disk I/O

Writes a bounded temporary file, fsyncs it, reads it back, and removes it.

### Process churn

Starts short-lived child processes within a configured cap.

### TCP listener

Starts a local TCP server on `127.0.0.1` using an ephemeral port and creates local client connections.

### HTTP local

Starts a temporary HTTP server bound only to `127.0.0.1` and issues local requests.

### Mixed

Runs a safe combination of CPU, memory, and disk I/O.

### Random

Chooses one scenario using the supplied seed. The chosen scenario is printed so it can be reproduced.

## Copy the script to a Linux test server

Copy:

```text
tools/linux_scenarios/random_linux_workload.py
```

to the test VM, or execute it from a checkout of this repository on that VM.

Requirements:

```text
Python 3.11+
no root privileges
no third-party Python packages
```

## Dry run

```bash
python3 random_linux_workload.py --scenario random --seed 20260811 --dry-run
```

## Run one reproducible random scenario

```bash
python3 random_linux_workload.py \
  --scenario random \
  --seed 20260811 \
  --duration 20
```

## Explicit CPU scenario

```bash
python3 random_linux_workload.py \
  --scenario cpu \
  --duration 30 \
  --cpu-workers 2
```

## Explicit memory scenario

```bash
python3 random_linux_workload.py \
  --scenario memory \
  --duration 20 \
  --memory-mb 128
```

## Disk I/O scenario

```bash
python3 random_linux_workload.py \
  --scenario disk-io \
  --duration 15 \
  --disk-mb 128
```

## Mixed scenario

```bash
python3 random_linux_workload.py \
  --scenario mixed \
  --duration 30 \
  --cpu-workers 2 \
  --memory-mb 128 \
  --disk-mb 128
```

## Run a deterministic matrix

Use:

```bash
python3 run_linux_scenario_matrix.py \
  --seed 20260811 \
  --duration 10
```

The matrix executes multiple bounded scenarios sequentially and writes a JSON result file.

## Recommended end-to-end workflow

On the Linux test VM:

```bash
python3 random_linux_workload.py --scenario random --seed 20260811 --duration 30
```

While or immediately after the workload is running, from the management
project, run normal monitoring through the application. Claude Code then uses
the current `vps` MCP workflow to inspect the created report/analysis and may
open the persisted Investigation route. The removed Python coordinator
acceptance path must not be used.

If an Investigation is persisted:

```powershell
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 500
uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500
```

## Recording a scenario

Always retain:

```text
server name / ID
scenario
seed
duration
resource limits
start/end timestamps
monitoring report ID
analysis ID
investigation ID, when one exists
```

The workload script prints a JSON summary suitable for attaching to test records.

## Operational warning

These workloads consume real CPU, memory, disk bandwidth, local sockets, and process slots. Use disposable or explicitly approved test servers.

Default caps are deliberately conservative, but operators remain responsible for selecting limits appropriate to the VM.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
