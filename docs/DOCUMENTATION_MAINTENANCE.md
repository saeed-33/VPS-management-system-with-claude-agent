# Documentation Maintenance

<!-- DOC-STATUS: CURRENT -->

## Canonical current state

Canonical project status is recorded in:

```text
docs/PROJECT_STATUS.md
docs/architecture/overview.md
docs/roadmap/phase-4-20-closeout.md
artifacts/evaluation/phase_4_20_readiness.json
```

## Historical documents

Past phase closeouts and ADRs are historical records. Their original implementation context should not be rewritten merely to make old dates/statuses look current.

Instead, every Markdown document receives a managed metadata block stating whether it is:

```text
CURRENT
HISTORICAL
DECISION
REFERENCE
```

## Sync commands

```powershell
uv run python tools/dev/generate_test_catalog.py
uv run python tools/dev/generate_project_structure.py
uv run python tools/dev/sync_documentation.py
uv run python tools/dev/audit_documentation.py
```

## Audit rules

The documentation audit checks:

- every Markdown document has a managed status block;
- active current documents do not contain known stale Phase 4.17/4.18 status language;
- all relative Markdown links resolve;
- the documentation inventory is regenerated from the actual checkout;
- canonical status remains `ready_for_supervised_operations`;
- automatic remediation remains false.

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
