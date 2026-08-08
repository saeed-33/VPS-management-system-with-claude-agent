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
  -f .\app\shared\database\migrations\step_4_6_investigation_persistence.sql
```

Acceptance:

```powershell
uv run python tools/bootstrap_database.py --verify-only
uv run python -m pytest
uv run python tools/persist_investigation_routing.py 807
uv run python tools/inspect_investigation.py <INVESTIGATION_ID>
```
