# Phase 4.19 Implementation Notes

## 4.19.1 — Investigation Read Models

Create a stable operator-facing read boundary.

Rules:

```text
API/UI do not consume SQLAlchemy models directly
API/UI do not consume Claude-supervised state directly
missing runtime data is explicit
no fabricated Specialist/Evidence/Diagnosis fields
```

## 4.19.2 — Runtime Snapshot Persistence

Next:

- serialize ServerCoordinatorResult;
- serialize Specialist runs;
- serialize Evidence;
- serialize correlated claims/conflicts;
- serialize FinalDiagnosis;
- serialize narrative/fallback state;
- update persisted Investigation status.

## 4.19.3 — Investigation API

Then:

```text
GET /api/investigations
GET /api/investigations/{investigation_id}
GET /api/reports/{report_id}/investigations
```

## 4.19.4 — Administration UI

Then add list/detail pages based only on the read/API contracts.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
