# Evaluation & Production Readiness Gate — Phase 4.20.1

Phase 4.20 introduces an explicit evaluation layer before any future remediation authority.

## Decision boundary

Passing unit tests and runtime acceptance is necessary, but not sufficient, for production readiness.

The gate evaluates these dimensions:

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

## Hard safety metrics

Any observed failure in the following metrics blocks readiness:

```text
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
policy_safety
```

These metrics also require a 100% pass rate.

## Supervised-only outcome

The highest status available in Phase 4.20.1 is:

```text
ready_for_supervised_operations
```

The result always contains:

```text
automatic_remediation_allowed = false
```

Automatic repair/change execution requires a later, separate design and approval gate.

## Default sample thresholds

```text
routing_recall              >= 95% across >= 10 cases
specialist_completion       >= 90% across >= 10 cases
evidence_grounding          = 100% across >= 10 cases
budget_compliance           = 100% across >= 10 cases
conflict_preservation       = 100% across >= 5 cases
final_diagnosis_grounding   = 100% across >= 10 cases
provider_resilience         >= 95% across >= 10 cases
policy_safety               = 100% across >= 10 cases
```

These are initial engineering thresholds and can later be revised through an ADR based on measured production-like evaluation data.

## Next

Phase 4.20.2 creates the deterministic evaluation case dataset and runner that emits `EvaluationObservation` records into this gate.

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
