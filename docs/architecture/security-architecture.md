# Security, Policy, and Audit Architecture

## Execution boundaries

SSH requires the configured private key and `known_hosts`; command execution
uses registered named commands and bounded adapters. Claude/MCP exposes zero
unrestricted raw SSH, raw SQL, arbitrary shell, or unrestricted filesystem
capabilities. The remediation registry is the only write path for supported
actions.

## Policy gates

The autonomous evaluator fails closed on disabled global state, missing or
ambiguous policy, unsupported action, risk above low, missing/failed/stale
sandbox, fingerprint mismatch, incomplete Evidence, missing rollback,
insufficient history, rate limits, cooldown, or circuit suspension. The three
outcomes are `AUTO_EXECUTE`, `REQUIRE_HUMAN_APPROVAL`, and `DENY`.

## Auth, RBAC, CSRF, and audit

`AdminAuthService` stores scrypt password verifiers, opaque server-side session
cookies whose digests are persisted, expiry/revocation state, and audit events.
Viewer has read permissions; Operator adds monitoring control and supervised
approval/execution/rollback; Admin adds management and autonomous policy
lifecycle permissions. Mutating cookie-authenticated requests require a valid
CSRF token. The middleware returns API 401/403 responses and redirects Web
requests to login when unauthenticated.

Audit is split by bounded context: Admin auth/security events,
`remediation_audit_events`, and `autonomous_policy_audit_events`. The Admin
Audit screen reads safe projections and deliberately omits session digests,
authorization tokens, reservation owner tokens, passwords, and private keys.

## Concurrency and recovery

Autonomous reservation creation is an atomic database operation keyed by
idempotency key. The owner token protects authorization attachment and final
state updates. The lease is short and is not held across Ollama, SSH,
verification, or rollback. Expired reservations can be reclaimed only when
the immutable operation binding matches. Finalization is conditional on the
owner token, preventing lost updates and stale workers from overwriting state.

The circuit breaker accounts terminal failures once, suspends the policy at
the configured consecutive-failure threshold, and requires an explicit
operator resume. Resume starts a durable new operator epoch; changing the
global switch does not resume a suspended policy.

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
