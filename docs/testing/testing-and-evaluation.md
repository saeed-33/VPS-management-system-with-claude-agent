# Testing and Evaluation

<!-- DOC-STATUS: CURRENT -->

## Current accepted state

```text
Phase 4.20: COMPLETE
C.14.12 readiness: 8 / 8 PASS
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

## Evaluation sources

Evaluation observations are classified as:

```text
DETERMINISTIC CONTROLLED EVALUATION
REAL RUNTIME
REAL PERSISTED RUNTIME
```

Controlled transport is used only to exercise deterministic provider and
failure behavior. It is not presented as a real runtime observation. The
C.14.12 artifact combines 30 controlled observations with 50 persisted runtime
observations and 11 runtime sessions.

## C.14.12 dimensions

| Metric | Accepted result | Threshold |
|---|---:|---:|
| routing_recall | 10/10, 1.000 PASS | 0.950 |
| specialist_completion | 10/10, 1.000 PASS | 0.900 |
| evidence_grounding | 10/10, 1.000 PASS | 1.000 |
| budget_compliance | 10/10, 1.000 PASS | 1.000 |
| conflict_preservation | 10/10, 1.000 PASS | 1.000 |
| final_diagnosis_grounding | 10/10, 1.000 PASS | 1.000 |
| provider_resilience | 10/10, 1.000 PASS | 0.950 |
| policy_safety | 10/10, 1.000 PASS | 1.000 |

Hard safety dimensions require a complete pass rate and fail closed.

## Commands

```powershell
uv run python tools/acceptance/run_safety_runtime_evaluation.py
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 100
uv run python tools/acceptance/run_production_readiness_evaluation.py \
  --server-id <server_id> --limit 100 \
  --output artifacts/evaluation/c14_12_readiness.json
```

The accepted evidence and latest real session are documented in
`docs/architecture/c14-12-runtime-readiness-gate.md`.

## Safety interpretation

Passing readiness means supervised diagnostic operations are ready. It does
not authorize automatic restart, process termination, package changes,
configuration writes, reboot, firewall changes, arbitrary shell, or production
remediation. Phase 5 requires separate contracts, approvals, sandbox and
rollback evidence.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
