# Testing Strategy

## Purpose

This project treats testing as a layered engineering system rather than a single `pytest` command.

The test strategy protects five different properties:

1. **Correctness** — deterministic code produces the expected result.
2. **Integration integrity** — repositories, services, API, web routes, Claude-supervised orchestration, and persistence remain compatible.
3. **Runtime validity** — real Ollama, SSH, diagnostic tools, Evidence, correlation, Final Diagnosis, and persistence work together.
4. **Safety** — Policy, budgets, grounding rules, provider failure handling, and conflict preservation fail closed.
5. **Operational readiness** — measured observations satisfy the Production Readiness Gate.

Phase 4.20 closed only after the aggregate gate reached:

```text
ready_for_supervised_operations
```

Automatic remediation remains explicitly disabled.

## Test pyramid used by the project

### Layer 1 — Unit and contract tests

Run all deterministic tests:

```powershell
uv run python -m pytest
```

Use this after every code change.

Focused examples:

```powershell
uv run python -m pytest tests/test_production_readiness_gate.py -v
uv run python -m pytest tests/test_evaluation_dataset_runner.py -v
uv run python -m pytest tests/test_persisted_runtime_evaluation.py -v
uv run python -m pytest tests/test_safety_runtime_evaluation.py -v
uv run python -m pytest tests/test_aggregate_readiness.py -v
```

### Layer 2 — API and web integration

The normal pytest suite includes FastAPI API/web tests.

Useful runtime inventories:

```powershell
uv run python tools/list_routes.py
```

Investigation read/API/UI acceptance:

```powershell
uv run python tools/run_investigation_web_api_acceptance.py --limit 25
```

### Layer 3 — Deterministic evaluation

Dataset coverage and gate wiring:

```powershell
uv run python tools/run_evaluation_dataset.py
```

This validates the evaluation dataset. It is not a runtime-quality score.

Controlled safety evaluation:

```powershell
uv run python tools/run_safety_runtime_evaluation.py
```

This exercises the real routing, Policy, and Ollama client logic with controlled provider transport.

### Layer 4 — Real runtime acceptance

These tests may contact real Linux servers and/or Ollama. Run them only in a controlled test environment.

Examples already present in the project may include:

```powershell
uv run python tools/run_server_coordinator_acceptance.py <report_id> --max-specialists 4 --max-rounds 3 --max-actions 12
uv run python tools/run_Claude-supervised_parallel_acceptance.py <report_id> --specialists linux-cpu,linux-memory --max-specialists 2 --max-rounds 2 --max-actions 8
uv run python tools/run_Claude-supervised_secondary_acceptance.py <report_id> --initial-specialist nginx --max-specialists 3 --max-rounds 3 --max-actions 10
uv run python tools/run_correlation_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
uv run python tools/run_final_diagnosis_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
uv run python tools/run_persisted_runtime_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
```

Not every checkout is guaranteed to contain every historical acceptance script. The generated `docs/testing/TEST_CATALOG.md` lists what actually exists in the current checkout.

### Layer 5 — Persisted runtime measurement

Evaluate real persisted Investigation snapshots:

```powershell
uv run python tools/run_persisted_runtime_evaluation.py --limit 500
```

This measures:

```text
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
```

### Layer 6 — Production Readiness Gate

Aggregate all measured observations:

```powershell
uv run python tools/run_production_readiness_evaluation.py --limit 500
```

Expected Phase 4 closeout state:

```text
Status: ready_for_supervised_operations
Automatic remediation: False
Production Readiness Gate: PASS
```

Machine-readable report:

```text
artifacts/evaluation/phase_4_20_readiness.json
```

## Required test sequence before merging

For ordinary code changes:

```text
1. focused tests for changed module
2. full pytest
3. relevant deterministic evaluation/acceptance tool
4. route inventory when API/web wiring changed
```

For Investigation/LLM/SSH/Claude-supervised orchestration changes:

```text
1. focused unit tests
2. full pytest
3. controlled safety/runtime acceptance
4. at least one real runtime acceptance against a disposable Linux test server
5. persisted-runtime evaluation
6. aggregate Production Readiness evaluation
```

For changes to Policy, Evidence validation, budgets, correlation, Final Diagnosis, or write-capable code:

```text
1. all normal requirements
2. controlled failure injection
3. explicit negative tests
4. verify no unknown Evidence/Knowledge IDs are accepted
5. verify DENY does not expose an executable command
6. verify action/round/global budgets cannot be exceeded
7. verify conflicts are preserved as unknown instead of silently resolved
8. verify automatic_remediation_allowed remains False
```

## Test data rules

Evaluation data must be classified as one of:

```text
DETERMINISTIC FIXTURE
CONTROLLED FAILURE INJECTION
REAL RUNTIME
REAL PERSISTED RUNTIME
```

Do not label fixture-only results as production measurements.

Controlled findings used to force conflict semantics must be backed by real runtime Evidence when used in persisted runtime acceptance.

## Reproducibility

Random Linux workload scripts support `--seed`. Always record:

```text
seed
scenario
duration
server
report/investigation ID
git commit
Ollama model/context
```

A failed random scenario is not actionable unless it can be reproduced or sufficient Evidence was persisted.

## Safety boundary

The Phase 4 test environment may execute only approved diagnostic operations and explicitly safe workload generators.

The random Linux scenario tools in `tools/linux_scenarios/`:

- do not install packages;
- do not modify firewall rules;
- do not restart system services;
- do not change system configuration;
- do not require root;
- create temporary files only under a selected temporary directory;
- cap CPU, memory, disk, duration, and process counts;
- clean up their own resources.

Do not run workload generators on production servers unless the operator has explicitly accepted the resource impact.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
