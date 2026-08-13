# Cross-Specialist Correlation — Phase 4.18

**Status:** 4.18.1 foundation implemented.

Phase 4.18 begins with a deterministic, provenance-first correlator before any global LLM synthesis is introduced.

## Certainty semantics

```text
confirmed
probable
unknown
```

Conservative baseline:

```text
live Evidence + confidence >= 0.80 -> confirmed
live Evidence + confidence < 0.80  -> probable
no live Evidence                   -> unknown
```

Knowledge references never upgrade a live server claim to confirmed.

## Provenance invariant

Every Evidence ID referenced by a correlated finding must exist in the server-level Investigation Evidence collection.

Unknown Evidence IDs fail closed.

## Correlation

Equivalent normalized finding titles from multiple Specialists are merged into one correlated claim.

The claim preserves source finding IDs, Specialist slugs, Evidence IDs, Knowledge source IDs, missing Evidence, and confidence.

## Next

4.18.2 adds conflict-aware final diagnosis synthesis while preserving this deterministic provenance envelope.
## 4.18.2 Conflict semantics

Conflict detection is explicit, not inferred from free-form prose.

A Specialist finding may attach:

```python
metadata={
    "diagnostic_state": "present"
}
```

When multiple findings correlate to the same topic and carry different non-empty `diagnostic_state` values, the correlator emits a `DiagnosisConflict`.

A conflicted claim is classified as:

```text
unknown
```

even if both source findings have high confidence and live Evidence.

This prevents a server-level diagnosis from silently selecting one Specialist over another.

Matching explicit states do not conflict.

If no `diagnostic_state` is supplied, the Phase 4.18.1 evidence-first certainty rules remain unchanged.

# Final Diagnosis Synthesis — Phase 4.18.4

Phase 4.18.4 adds an optional LLM-assisted narrative layer above the deterministic `FinalDiagnosis`.

## Trust boundary

The LLM does not receive authority to change the diagnosis envelope.

It cannot:

- create a new claim;
- change confirmed/probable/unknown;
- create an Evidence ID;
- remove an unresolved conflict;
- authorize diagnostic execution.

The LLM may only return:

```text
summary
claim_ids
conflict_ids
operator_notes
```

Every returned ID is validated against the deterministic diagnosis.

## Fallback

If the provider fails, returns invalid structured output, references an unknown claim/conflict, or omits an existing conflict, synthesis falls back to the deterministic correlation summary.

A narrative failure therefore does not invalidate the Investigation.

## Provider behavior

Ollama uses:

```text
format=json
num_ctx=32768
num_predict=4096
temperature=0
```

The smaller output budget is intentional for this narrative-only payload; it is separate from Specialist reasoning generation limits.

Ollama uses parsed structured output with the same narrative schema.

## Next

Phase 4.18.5 performs runtime acceptance using a real Final Diagnosis and the configured LLM provider, including deterministic fallback validation.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
