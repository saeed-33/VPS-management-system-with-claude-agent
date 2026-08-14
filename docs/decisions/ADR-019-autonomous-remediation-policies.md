# ADR-019: Persisted autonomous remediation policies

## Decision

Introduce a separate Phase 7 policy/evaluation/authorization layer. Reuse the
existing Phase 5 `RemediationService` for the actual registered write,
Evidence collection, verification, rollback, and audit sink. Do not let an
LLM authorize itself and do not keep a database transaction open during
external execution.

## Reasons

Replacing the complete `investigation_metadata` JSON or reading and writing a
whole snapshot would permit lost updates. Phase 7 therefore uses row-level
policy/decision/reservation records, unique idempotency keys, a reservation
lease, and finalization after execution. Policy version, plan fingerprint,
server, action, target, and sandbox validation are all checked again before
the named write.

## Consequences

The default remains disabled and an operator must explicitly enable a policy.
The V1 surface is intentionally small: `start_service` on an explicit service
target at low risk. Runtime state records consecutive failures and can
automatically suspend a policy; only Admin can resume it. Existing supervised
operations retain their original approval path.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

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
