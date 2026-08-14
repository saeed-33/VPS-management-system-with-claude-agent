# Runtime Snapshot Persistence — Phase 4.19.2

Phase 4.19.2 persists an operator-facing projection of accepted Investigation runtime state.

The snapshot is stored under:

```text
investigations.metadata.runtime_snapshot
```

This is intentionally a read projection rather than a replacement for Claude-supervised runtime state.

## Persisted envelope

```text
status
orchestrator
execution_mode
waves_completed
actions_used
evidence_count
specialist_runs[]
evidence[]
correlated_claims[]
conflicts[]
final_diagnosis
narrative
metadata
```

Existing Investigation metadata is preserved.

The persisted Investigation `status` is updated from the runtime state.

## Provenance

Evidence IDs, claim IDs, conflict IDs, Specialist identities, certainty values, and narrative fallback state are serialized without re-reasoning.

The snapshot service does not create new claims or Evidence.

## Storage decision

No database migration is required in 4.19.2 because the existing Investigation metadata column is JSON.

This is suitable for the current operator read model and avoids premature schema proliferation.

If runtime history, large Evidence payloads, or high-volume querying later require relational storage, that becomes a separate persistence ADR/migration rather than silently changing this contract.

## Next

Phase 4.19.3 exposes the read models through read-only Investigation API endpoints.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

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
