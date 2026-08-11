# Testing and Evaluation

<!-- DOC-STATUS: CURRENT -->

## Current accepted state

Phase 4.20 is complete.

```text
Production Readiness Gate: PASS
Readiness: ready_for_supervised_operations
Automatic remediation: False
```

Reference regression baseline immediately before documentation closeout:

```text
237 passed, 1 warning
```

## Testing model

The project uses six complementary test layers.

```text
1. unit / contract
2. API / web / persistence integration
3. deterministic evaluation
4. controlled failure injection
5. real runtime acceptance
6. aggregate production-readiness evaluation
```

Passing `pytest` alone is necessary but not sufficient for Investigation/LLM/SSH changes.

## Unit and contract suite

```powershell
uv run python -m pytest
```

The suite covers, among other areas:

```text
Investigation contracts
routing
Specialist registry
Specialist context
reasoning contracts
Ollama compatibility
Knowledge ingestion/chunking/indexing/retrieval
Diagnostic Tool Registry
Policy
Evidence collection
Specialist loop
Server Coordinator
Claude-supervised parallel orchestration
dynamic secondary routing
correlation/conflicts
Final Diagnosis
runtime snapshot persistence
Investigation API/UI
evaluation dataset
persisted runtime evaluation
safety runtime evaluation
readiness gate
aggregate readiness
```

## Deterministic evaluation

Dataset coverage:

```powershell
uv run python tools/run_evaluation_dataset.py
```

This verifies dataset/gate wiring only.

Safety/runtime controlled evaluation:

```powershell
uv run python tools/run_safety_runtime_evaluation.py
```

This executes real routing and Policy logic and real Ollama-client parsing/retry/failure behavior through controlled HTTP transport.

## Real runtime acceptance

Real runtime tests may contact Ollama and Linux hosts over SSH.

Examples:

```powershell
uv run python tools/run_server_coordinator_acceptance.py <report_id> --max-specialists 4 --max-rounds 3 --max-actions 12
uv run python tools/run_Claude-supervised_parallel_acceptance.py <report_id> --specialists linux-cpu,linux-memory --max-specialists 2 --max-rounds 2 --max-actions 8
uv run python tools/run_Claude-supervised_secondary_acceptance.py <report_id> --initial-specialist nginx --max-specialists 3 --max-rounds 3 --max-actions 10
uv run python tools/run_correlation_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
uv run python tools/run_final_diagnosis_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
uv run python tools/run_persisted_runtime_acceptance.py <report_id> --initial-specialist nginx --secondary-specialist systemd-service --max-rounds 3 --max-actions 10
```

Use `docs/testing/TEST_CATALOG.md` for the exact tools/tests available in the current checkout.

## Persisted runtime measurement

```powershell
uv run python tools/run_persisted_runtime_evaluation.py --limit 500
```

Measured from persisted real snapshots:

```text
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
```

## Production readiness

```powershell
uv run python tools/run_production_readiness_evaluation.py --limit 500
```

Current accepted result:

```text
routing_recall                 PASS
specialist_completion          PASS
evidence_grounding             PASS
budget_compliance              PASS
conflict_preservation          PASS
final_diagnosis_grounding      PASS
provider_resilience            PASS
policy_safety                  PASS
```

## Random Linux scenarios

See `RUNTIME_SCENARIOS.md`.

Use seeded workloads on disposable Linux test servers:

```bash
python3 tools/linux_scenarios/random_linux_workload.py \
  --scenario random \
  --seed 20260811 \
  --duration 20
```

Always retain seed, scenario, report ID, Investigation ID, commit, and model/context.

## Required merge discipline

Ordinary changes:

```text
focused tests
full pytest
relevant acceptance
route inventory if API/web changed
```

Investigation/LLM/SSH/Policy changes:

```text
focused tests
full pytest
controlled safety tests
real runtime acceptance
persisted runtime evaluation
aggregate readiness evaluation
```

Write-capable Phase 5 work must add separate approval/rollback tests before implementation is considered safe.

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
