# Phase 4.19 Implementation Notes

## 4.19.1 — Investigation Read Models

Create a stable operator-facing read boundary.

Rules:

```text
API/UI do not consume SQLAlchemy models directly
API/UI do not consume LangGraph state directly
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
