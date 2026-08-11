# Persisted Runtime Evaluation — Phase 4.20.3

Phase 4.20.3 starts measuring real Investigation outputs.

It evaluates persisted runtime snapshots instead of re-running expensive runtime operations.

## Measured from persisted state

For every Investigation with `runtime_available=true`, the evaluator emits actual observations for:

```text
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
```

These observations are derived from real persisted Specialist runs, Evidence, claims, conflicts, Final Diagnosis, and narrative references.

## Not measured here

The following metrics cannot be honestly established from a persisted runtime snapshot alone:

```text
routing_recall
provider_resilience
policy_safety
```

They remain missing and therefore keep the Production Readiness Gate in `insufficient_evidence` until Phase 4.20.4 supplies controlled runtime/failure observations.

## Safety rule

Missing metrics are never converted to passing observations.

This prevents dataset coverage from being confused with measured runtime quality.

## Next

Phase 4.20.4 adds controlled runtime/failure injection for routing, provider resilience, Policy safety, and critical failure behavior.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
