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

The five additive tables are created by
`app/infrastructure/database/migrations/step_7_1_autonomous_remediation.sql`.
`tools/bootstrap_database.py --verify-only` is the schema check and reports
29/29 tables in the current project database.

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
