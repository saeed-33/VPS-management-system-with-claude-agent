# Concurrency and Recovery Testing

The deterministic recovery harness creates competing reservation attempts,
reclaims expired leases, attaches authorization with an owner token, finalizes
with the owner token, simulates interrupted jobs, and exercises circuit
breaker recovery. The acceptance property is that an immutable idempotency
binding cannot physically execute more than once and a stale worker cannot
overwrite the current reservation state.

Relevant tests include `tests/acceptance/readiness/test_autonomous_concurrency_recovery.py`,
`tests/unit/capabilities/remediation/test_autonomous_execution_idempotency.py`,
`tests/acceptance/readiness/test_autonomous_circuit_breaker.py`,
and `tests/unit/runtime/claude/test_agent_job_persistence.py`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
