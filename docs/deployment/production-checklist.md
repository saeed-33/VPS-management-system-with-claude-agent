# Production / Supervised Operations Checklist

<!-- DOC-STATUS: CURRENT -->

This checklist applies to the current Phase 4 system, which is approved only for supervised diagnostic operations.

## Required state

```text
Production Readiness Gate = PASS
readiness = ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Application

- Environment variables validated.
- Database reachable.
- Required migrations applied.
- FastAPI health endpoint succeeds.
- Route inventory matches expected API/web surface.
- Scheduler configuration reviewed.
- Secrets are not committed.

## Ollama / LLM

- Configured provider reachable when LLM is enabled.
- Model name verified.
- Runtime context explicitly configured.
- Structured-output compatibility/retry path tested.
- Provider failure is fail-safe.

Reference accepted local model family during Phase 4 testing:

```text
gemma4:e4b-it-q4_K_M
context 32768
```

This is a reference, not a hard requirement for every deployment.

## Linux / SSH

- Test connection succeeds for monitored servers.
- Monitoring user privileges are least-privilege.
- No arbitrary shell capability is exposed to the model.
- Diagnostic Tool Registry contains only reviewed tools.
- Policy DENY cannot reach SSH execution.

## Evaluation

Run:

```powershell
uv run python -m pytest
uv run python tools/acceptance/run_evaluation_dataset.py
uv run python tools/acceptance/run_safety_runtime_evaluation.py
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 500
uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500
```

The final command must report:

```text
Production Readiness Gate: PASS
```

## Operational restrictions

The Phase 4 system is read-only diagnostic automation.

Do not enable or manually wire in write-capable actions such as restart, kill, package changes, configuration writes, firewall changes, or reboot.

Such capabilities belong to Phase 5 supervised remediation with separate approval and rollback design.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **OPERATIONS**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
