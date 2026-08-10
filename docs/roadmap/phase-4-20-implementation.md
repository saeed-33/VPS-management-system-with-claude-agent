# Phase 4.20 — Evaluation, Safety & Production Readiness

## 4.20.1 — Evaluation Contracts & Readiness Gate

Status: implementation step.

Introduce a deterministic gate above the accepted Investigation architecture.

The gate must distinguish:

```text
insufficient_evidence
blocked
ready_for_supervised_operations
```

It must never imply automatic remediation authority.

## 4.20.2 — Evaluation Dataset & Runner

Build repeatable cases covering:

- routing/no-routing;
- correct Specialist selection;
- evidence grounding;
- unknown Evidence rejection;
- budget limits;
- duplicate tool suppression;
- explicit conflicts;
- provider failure/fallback;
- Policy ALLOW/DENY boundaries;
- persisted Final Diagnosis provenance.

The runner emits observations only; it does not change production state.

## 4.20.3 — Runtime Evaluation Report

Run the evaluation suite against the configured provider/runtime and produce a machine-readable and operator-readable report.

## 4.20.4 — Safety Failure Injection

Exercise controlled failures:

```text
SSH unavailable
provider invalid JSON
provider timeout
tool denied by Policy
tool returns non-zero
unknown Evidence ID
unknown Knowledge ID
budget exhausted
conflicting Specialist conclusions
```

## 4.20.5 — Production Readiness Acceptance

The readiness gate consumes the measured observations.

Only `ready_for_supervised_operations` closes Phase 4.20.

Automatic remediation remains out of scope and disabled.
