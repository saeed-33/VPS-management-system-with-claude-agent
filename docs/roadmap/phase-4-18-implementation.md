# Phase 4.18 Implementation Notes

## 4.18.1 — Correlation foundation

Add deterministic correlation contracts and a provenance-first correlator.

Acceptance:

```text
high-confidence Evidence claim -> confirmed
lower-confidence Evidence claim -> probable
Knowledge-only claim -> unknown
matching findings merge Specialists
unknown Evidence reference -> fail closed
```

## 4.18.2 — Conflict-aware final synthesis

Next:

- explicit contradiction representation;
- correlate positive/negative findings;
- server-level final summary;
- optional LLM synthesis over validated correlated claims;
- no invented Evidence or Knowledge IDs.

## 4.18.3 — Runtime acceptance

Use at least two completed Specialists, a shared Evidence-backed conclusion, a conflicting or insufficient Evidence scenario, and full claim-to-Evidence traceability.
## 4.18.2 — Completed design target

Conflict-aware correlation adds:

- `DiagnosisConflict`
- explicit `diagnostic_state`
- conflict count on `FinalDiagnosis`
- conflict forces certainty to `unknown`
- no prose-based negation inference

### Next: 4.18.3 Runtime acceptance

The runtime acceptance must exercise at least two Specialist results and verify:

```text
shared conclusion -> merged claim
explicit contradiction -> conflict
conflict -> unknown
Evidence IDs preserved
no unsupported final claim
```

## 4.18.4 — LLM-assisted Final Diagnosis narrative

Status: implementation step.

The deterministic correlator remains authoritative.

The narrative synthesizer may:

```text
summarize
order existing claim IDs
order existing conflict IDs
produce short operator notes
```

It may not mutate certainty or provenance.

Any provider/validation failure returns the deterministic fallback narrative.

### Next: 4.18.5 runtime acceptance

Acceptance must prove:

```text
real provider narrative succeeds OR safe fallback occurs
no invented claim IDs accepted
no invented conflict IDs accepted
existing conflicts cannot be omitted
deterministic diagnosis remains available
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
