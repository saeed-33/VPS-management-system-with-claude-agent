# Admin Management Coverage

At the current Phase boundary, operator-owned configuration must be manageable from the Admin UI.

## Dynamic Specialists

`/specialists` manages Specialist definitions, including `allowed_tool_ids`.
Allowed Tool IDs are selected from the actual read-only Diagnostic Tool Registry exposed by `GET /api/diagnostic-tools`; operators do not type unregistered Tool IDs.

## Knowledge Sources

`/knowledge-sources` manages create/edit/delete, enable/disable, source type, URI/inline content, domains, Specialist scope, tags and priority.
Knowledge Source definition management is separate from ingestion/indexing.

## Deliberately internal for now

RRF/HNSW/index tuning, embeddings, context-building internals and reasoning prompts remain internal. Investigation timeline/evidence/result UI remains planned for Phase 4.19.

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
