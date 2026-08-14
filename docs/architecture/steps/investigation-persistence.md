# Investigation Persistence

**Phase:** 4.6  
**Status:** Implemented — pending migration/runtime acceptance

Phase 4.6 persists the routing snapshot before Specialist execution exists.

```text
Report + Analysis
 -> InvestigationRouter
 -> candidate_specialists
 -> selected_specialists
 -> InvestigationPersistenceService
 -> PostgreSQL
```

Tables:

```text
investigations
investigation_specialist_candidates
```

The candidate table preserves the full candidate order and independently
stores `is_selected` and `selected_rank`.

Specialist slug/name are snapshotted. The optional FK to
`specialist_definitions` uses `ON DELETE SET NULL`, so historical
investigations remain readable after later Specialist deletion.

This step does not yet persist Specialist tasks/results/evidence.

Migration:

```powershell
psql -U <POSTGRES_USER> -d <POSTGRES_DB> `
  -f .\app\infrastructure\database\migrations\step_4_6_investigation_persistence.sql
```

Acceptance:

```powershell
uv run python tools/bootstrap_database.py --verify-only
uv run python -m pytest
uv run python tools/dev/persist_investigation_routing.py 807
uv run python tools/dev/inspect_investigation.py <INVESTIGATION_ID>
```

> Historical document — not current architecture.

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
