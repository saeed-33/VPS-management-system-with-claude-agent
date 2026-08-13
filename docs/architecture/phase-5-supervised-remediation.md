# Phase 5 — Supervised Remediation Architecture

Phase 5 adds a supervised remediation lifecycle while keeping automatic
remediation disabled:

```text
diagnosis + Evidence -> proposal -> immutable plan + fingerprint
 -> sandbox -> persisted approval -> human decision
 -> immediate policy/fingerprint recheck -> named write
 -> before/after Evidence -> verification -> success or rollback-required
```

`app/core/contracts/remediation.py` owns lifecycle states, approval and
execution statuses, structured actions, and canonical plan fingerprints.
Actions contain a named tool and validated target; raw command text is not a
contract field.

`app/core/policies/remediation_tools.py` is the strict write registry. The
current registered actions are `start_service`, `stop_service`,
`restart_service`, and `reload_service`. Service names are allow-listed by
grammar and command strings are built only inside the registry.

`RemediationRiskClassifier` is deterministic and can raise risk for tagged
production/critical servers. Unknown actions are never executable.

The additive migration
`app/infrastructure/database/migrations/step_5_1_supervised_remediation.sql`
adds plan fingerprint/state columns and creates approval, execution,
verification, rollback, audit-event, and project-owned service-state Evidence
tables. Existing Phase C plans and sandbox results are preserved.
`tools/bootstrap_database.py` verifies all 24 required tables, including the
additive Phase 6 `sandbox_validations` table.

Every lifecycle boundary writes a project-owned audit event carrying plan,
server, actor, session/job correlation where available, and structured
payload. Admin and MCP adapters use the same service; no second orchestration
engine exists.

Execution requires a persisted approval ID, matching immutable fingerprint,
original server ID, unexpired approval, sandbox pass, registered action,
registered rollback, project-owned before/after Evidence, and available
verification. `start_service` is reversible only when before Evidence proves
the service was inactive, using `stop_service`; `stop_service` is reversible
only when before Evidence proves it was active, using `start_service`.
`restart_service` and `reload_service` have no rollback action because
repeating either operation does not restore a prior known process/configuration
state. The policy is rechecked immediately before execution. A unique
idempotency key prevents a second write.

The production composition uses the existing known-hosts SSH client and
command executor behind a named-write adapter. Raw SSH, arbitrary shell, and
generic command input are not exposed to Claude, MCP, or Admin.

The `server-supervisor` may propose, create, sandbox, request approval, and
submit an already approved execution. `specialist-worker` has no remediation
tools. Admin provides plan, approval, execution, rollback, and audit views;
actor identity is explicit because this repository has no authentication/RBAC
layer.

The public MCP inventory remains 24 tools and public names are unchanged.
Phase 5 enriches the existing six remediation tools rather than adding a
second facade.

The readiness evaluator emitted all 13 required metrics with numerator,
denominator, score, threshold, and pass/fail state. Phase 5 real acceptance
passed on the explicitly designated non-production `phase5-lab` target (server
4), restored the service to its initial state, and Phase 5 is closed. Phase 6
adds the fingerprint-bound Claude-native isolated validation gate before the
approval step; its real acceptance remains blocked until native sandbox
attestation is available.

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
