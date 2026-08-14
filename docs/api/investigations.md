# Investigation API

<!-- DOC-STATUS: CURRENT -->

The Investigation API is read-only.

## Endpoints

```text
GET /api/investigations
GET /api/investigations/{investigation_id}
GET /api/reports/{report_id}/investigations
```

## List semantics

The list endpoint returns persisted Investigation summaries and runtime/final-diagnosis availability flags where supported by the read model.

## Detail semantics

The detail endpoint may expose:

```text
identity
server/report/analysis IDs
routing decision
budgets
status
runtime availability
Specialist runs
Evidence
correlated claims
conflicts
Final Diagnosis
narrative
metadata
timestamps
```

The API does not execute Specialists or remediation.

## Provenance

Persisted Claim/Conflict/Narrative references must remain valid against the runtime snapshot.

## UI

Read-only administration pages consume the Investigation read model:

```text
GET /investigations
GET /investigations/{investigation_id}
```

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
