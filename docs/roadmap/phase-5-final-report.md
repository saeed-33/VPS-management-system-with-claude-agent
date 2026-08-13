# Phase 5 — Supervised Remediation Final Report

## 1. Starting State

- Commit: `b425c3619cea681061780c3034e82354e6cd4c5e`.
- Initial working tree: clean.
- Phase C baseline: C.14.11A/C.14.12/C.14.13/C.14.14 PASS; Phase C CLOSED.
- Initial normal suite: 417 passed, 1 skipped, 1 warning.

## 2. Phase 5.1 Contracts

Implemented structured actions, lifecycle statuses, approval/execution/
verification/rollback statuses, fingerprints, and normal `no_solution_found`.

## 3. Phase 5.2 Persistence

Added additive plan state columns and approval, execution, verification,
rollback, and audit tables/repository operations. The operational schema now
verifies 22/22 required tables.

## 4. Phase 5.3 Proposal Service

Plans preserve investigation, diagnosis, Evidence, server, actions, risk, and
production-disabled metadata. Unsupported executable actions fail sandbox or
execution validation; no-solution is persisted as a normal outcome.

## 5. Phase 5.4 Risk Classification

Deterministic registry-based risk classification supports LOW/MEDIUM/HIGH/
CRITICAL and raises risk for critical/production server tags.

## 6. Phase 5.5 Human Approval

Approval is persisted with actor, decision, comment, scope, expiry, and an
immutable plan fingerprint. Rejection, expiry, stale fingerprints, and
wrong-server execution are denied.

## 7. Phase 5.6 Registered Write Tools

| Tool | Parameters | Risk | Verification | Rollback | Policy |
|---|---|---|---|---|---|
| `start_service` | validated service name | medium | service active | `stop_service` | approval + original server |
| `stop_service` | validated service name | high | service inactive | `start_service` | approval + original server |
| `restart_service` | validated service name | high | service active | registered restart | approval + original server |
| `reload_service` | validated service name | medium | service active | registered reload | approval + original server |

No raw command field or generic shell write tool exists.

## 8. Phase 5.7 Policy Engine

Policy checks registration, server binding, risk lifecycle, approval status,
fingerprint, expiry, rollback, verification, and automatic-remediation mode.
It fails closed.

## 9. Phase 5.8 Controlled Execution

Execution uses the existing known-hosts SSH infrastructure through a named
adapter. Approval is rechecked immediately before the write. Unique
idempotency keys and a database uniqueness guard prevent duplicate execution;
interrupted execution is marked blocked for operator review and never replayed.

## 10. Phase 5.9 Evidence

Execution records before/after Evidence IDs and never accepts caller-supplied
raw before/after state. The SSH adapter uses fixed service-state commands;
Evidence ownership remains project-owned.

## 11. Phase 5.10 Verification

Verification runs after execution and requires the expected service state.
Exit-zero with an unhealthy after-state is not success.

## 12. Phase 5.11 Rollback

Registered reverse service actions are used only where declared supported.
Rollback outcomes and Evidence links are persisted; rollback failure remains an
explicit `rollback_failed` state.

## 13. Phase 5.12 Claude Integration

The server supervisor may propose, create, sandbox, request approval, and
submit an already approved execution. Python enforces approval and policy.
The specialist worker remains diagnostic-only. No second orchestration engine
was introduced.

## 14. Phase 5.13 Admin API/UI

Added plan, approval, rejection, execution, rollback, and audit API routes plus
a Jinja operator page. HIGH/CRITICAL approval and execution require deliberate
confirmation. Authentication/RBAC is not claimed; actor identity is explicit.

## 15. Phase 5.14 Audit / Events

Lifecycle events persist plan/server/actor/session/job correlation, payload, and
timestamps. Transport-neutral event contracts exist; Telegram was not added.

## 16. MCP Surface

- Previous tool count: 24.
- Final tool count: 24.
- Tools added: none.
- Tools removed: none.
- Existing six remediation tools were normalized.
- Raw shell/SSH/SQL exposure: none; raw escape paths remain denied.

## 17. Safety Test Results

Focused tests pass for injection attempts, missing/rejected/expired approval,
stale/wrong-server protection, unknown tools, duplicate execution, execution
failure, verification false-positive prevention, rollback success/failure,
Admin route/UI registration, and Claude least privilege. Existing SSH timeout
and connection failure tests remain green.

## 18. Phase 5 Readiness Metrics

| Metric | Numerator | Denominator | Score | Threshold | Result |
|---|---:|---:|---:|---:|---|
| proposal_validity | 1 | 1 | 1.000 | 1.000 | PASS |
| risk_classification | 1 | 1 | 1.000 | 1.000 | PASS |
| approval_integrity | 1 | 1 | 1.000 | 1.000 | PASS |
| policy_enforcement | 1 | 1 | 1.000 | 1.000 | PASS |
| write_tool_safety | 1 | 1 | 1.000 | 1.000 | PASS |
| execution_integrity | 1 | 1 | 1.000 | 1.000 | PASS |
| idempotency | 1 | 1 | 1.000 | 1.000 | PASS |
| evidence_completeness | 1 | 1 | 1.000 | 1.000 | PASS |
| verification_correctness | 1 | 1 | 1.000 | 1.000 | PASS |
| rollback_correctness | 1 | 1 | 1.000 | 1.000 | PASS |
| audit_completeness | 1 | 1 | 1.000 | 1.000 | PASS |
| mcp_safety | 1 | 1 | 1.000 | 1.000 | PASS |
| real_supervised_remediation | 0 | 1 | 0.000 | 1.000 | FAIL |

## 19. Full Test Result

`428 passed, 1 skipped, 1 warning in 13.92s`.

## 20. Real Supervised Remediation Acceptance

`BLOCKED_BY_SAFE_TEST_ENVIRONMENT`. The configured `vm1` and `vm2` records are
offline and neither is explicitly designated as a safe reversible target. No
real write was attempted.

## 21. Automatic Remediation State

`automatic_remediation_allowed = false`.

## 22. Remaining Technical Debt

- Designate an explicitly safe low-risk reversible test target and run the
  opt-in real acceptance.
- Add deployment authentication/RBAC before treating Admin approval as
  production-grade multi-user authorization.

## 23. Phase 5 Gate Decision

PHASE 5 = NOT CLOSED

## 24. Next Allowed Step

No Phase 6 step is allowed. First resolve the safe-test-environment blocker
and rerun the real supervised-remediation acceptance.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **ROADMAP**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
