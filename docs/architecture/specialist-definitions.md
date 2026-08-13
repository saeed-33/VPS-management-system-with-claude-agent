# Dynamic Specialist Definitions

**Phase:** 4.2  
**Status:** Implemented — pending migration/test verification

Specialists are persisted user-defined runtime data. Python does not contain a closed CPU/Memory/PostgreSQL catalog.

The new `specialist_definitions` table stores:

```text
slug, name, description, instructions, enabled,
domains, trigger_hints, knowledge_topics, allowed_tool_ids,
priority, max_rounds, max_actions, metadata,
created_at, updated_at
```

`slug` is normalized lowercase and unique. It remains dynamic, not a Python enum.

`domains`, `trigger_hints`, `knowledge_topics`, and `allowed_tool_ids` are JSON arrays in this baseline. Tool IDs are references only; validation against the future Tool Registry belongs to Phase 4.11.

Per-specialist defaults:

```text
max_rounds = 2
max_actions = 4
```

The global `InvestigationBudget` from 4.1 remains a separate upper-level constraint.

`instructions` do not grant capabilities. Future execution still requires registered tools and policy approval.

Apply the migration:

```powershell
psql -U <POSTGRES_USER> -d <POSTGRES_DB> `
  -f .\app\infrastructure\database\migrations\step_4_2_specialist_definitions.sql
```

Then:

```powershell
uv run python -m pytest
uv run python tools/bootstrap_database.py --verify-only
```

No API or UI is added in 4.2; those belong to 4.3.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
