# Admin Management Coverage

At the current Phase boundary, operator-owned configuration must be manageable from the Admin UI.

## Dynamic Specialists

`/specialists` manages Specialist definitions, including `allowed_tool_ids`.
Allowed Tool IDs are selected from the actual read-only Diagnostic Tool Registry exposed by `GET /api/diagnostic-tools`; operators do not type unregistered Tool IDs.

## Knowledge Sources

`/knowledge-sources` manages create/edit/delete, enable/disable, source type, URI/inline content, domains, Specialist scope, tags and priority.
Knowledge Source definition management is separate from ingestion/indexing.

## Deliberately internal for now

RRF/HNSW/index tuning, embeddings, context-building internals and reasoning
prompts remain internal. Investigation timeline, Evidence, and result views
are available through the current read-only Investigation API and Admin UI.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
