# ADR-016 — Production Readiness Gate and Remediation Boundary

<!-- DOC-STATUS: CURRENT -->

## Status

Accepted.

## Context

The Investigation architecture can execute real read-only diagnostic operations through Claude-supervised, Specialists, Policy, SSH tools, Evidence collection, correlation, Final Diagnosis, persistence, API, and UI.

Successful runtime acceptance alone is insufficient to authorize operational use or future write-capable actions.

## Decision

Introduce a deterministic Production Readiness Gate with explicit measured metrics:

```text
routing_recall
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
provider_resilience
policy_safety
```

The highest Phase 4 state is:

```text
ready_for_supervised_operations
```

Phase 4 always returns:

```text
automatic_remediation_allowed = false
```

## Safety metrics

The following are hard-block metrics and require 100% pass rate:

```text
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
policy_safety
```

## Consequences

Phase 4 may be used for supervised diagnosis after the gate passes.

Phase 4 may not restart services, kill processes, edit configuration, install/remove packages, reboot systems, change firewall rules, or expose arbitrary shell.

Phase 5 requires a new ADR/contract set for remediation plans, approval, audit, before/after Evidence, verification, and rollback.

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
