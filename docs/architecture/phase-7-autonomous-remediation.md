# Phase 7 — Autonomous Remediation Policies

Phase 7 adds a deterministic, persisted policy layer above the Phase 5/6
remediation lifecycle. It does not replace Evidence collection, sandbox
validation, verification, rollback, or the named write-tool registry.

The default is fail-closed:

```text
AUTOMATIC_REMEDIATION_ALLOWED=false
V1 action allowlist=start_service
V1 risk ceiling=low
```

An eligible operation follows:

```text
evaluate persisted plan and Evidence
  -> reserve idempotency key with a short lease
  -> issue and consume single-use authorization
  -> revalidate plan/policy/sandbox bindings
  -> execute existing Phase 5 named action outside the reservation transaction
  -> collect existing Before/After Evidence and verify
  -> finalize reservation and update circuit-breaker state
```

The reservation transaction is never held across SSH or Ollama work. The
database owns policy versions, decisions, authorizations, reservations,
runtime state, history queries, and rate-limit counters. An expired lease can
be reclaimed only for the same idempotency binding; a different operation
using the key is rejected.

Policies are created, edited, enabled, disabled, suspended, and resumed only
through the Admin boundary. Claude can call the bounded attempt tool, but it
cannot create or alter policy, resume a policy, change the global switch, or
pass a target/action outside the hard allowlist.

## Issue identity versus plan identity

`issue_fingerprint` is derived by Python from the persisted structured
`correlated_claims` diagnosis fields: normalized claim `title`, `certainty`,
and normalized sorted `metadata.diagnostic_states`. The payload is versioned
as `issue-fingerprint-v1`, serialized with stable sorted JSON, and hashed with
SHA-256. Claim IDs, finding IDs, Evidence IDs, narrative text, confidence,
timestamps, provider/model/session/job IDs, and plan identity are excluded.

`plan_fingerprint` remains the exact immutable binding for one plan version,
including its plan ID, server, actions, and Evidence IDs. A missing trusted
issue fingerprint never falls back to `plan_fingerprint`: Phase 7 returns
`require_human_approval` with `issue_fingerprint_missing`, while supervised
remediation remains available. Legacy plans are readable but are excluded
from autonomous history and candidate aggregation.

The six additive tables are created by
`app/infrastructure/database/migrations/step_7_1_autonomous_remediation.sql`.
`tools/bootstrap_database.py --verify-only` is the schema check and reports
30/30 tables in the current project database.

## Deterministic gates

Autonomous execution requires all of the following: global enablement, one
unambiguous enabled policy, exact issue fingerprint/action/target/server
binding, low risk, a ready plan, diagnosis and plan Evidence links, a passed
fresh sandbox with matching Before/After Evidence and verification, rollback
support, sufficient verified supervised history, acceptable failure and
rollback-failure rates, cooldown/rate limits, and no circuit-breaker pause.
Missing policy falls back to human approval only when the safety baseline is
present. Missing or failed sandbox, ambiguous policy, stale binding, and all
hard-deny conditions remain denied.

V1 uses a consecutive-failure circuit breaker with a default threshold of
one and `auto_suspend_on_failure=true`. The terminal execution path records
the failure atomically with runtime state and policy suspension; the
reservation is not held open during SSH, verification, or rollback. A
successful execution resets the runtime count only in an enabled operator
epoch. Operator resume is explicit, durable, and audited; changing the
global switch never resumes a suspended policy.
