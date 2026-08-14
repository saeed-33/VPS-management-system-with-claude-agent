# Specialists Management API

**Phase:** 4.3

The specialist-definition API manages user-defined runtime specialist definitions. It does not start investigations or invoke an LLM.

## Endpoints

```text
GET    /api/specialists
GET    /api/specialists/{id}
POST   /api/specialists
PATCH  /api/specialists/{id}
PUT    /api/specialists/{id}/enabled
DELETE /api/specialists/{id}
```

`GET /api/specialists?enabled_only=true` returns only enabled definitions.

## Stable identity

`slug` is accepted at creation and is deliberately not part of the update contract. Future investigation tasks and registry lookups need a stable specialist identifier.

## Create payload

```json
{
  "slug": "cpu",
  "name": "Linux CPU Investigator",
  "description": "Investigates CPU saturation.",
  "instructions": "Focus on CPU evidence.",
  "enabled": true,
  "domains": ["cpu", "process"],
  "trigger_hints": ["high cpu"],
  "knowledge_topics": ["linux cpu"],
  "allowed_tool_ids": [],
  "priority": 100,
  "max_rounds": 2,
  "max_actions": 4,
  "metadata": {}
}
```

Duplicate slug returns `409`.
Missing IDs return `404`.
Request validation errors return `422`.

## UI

The admin page is:

```text
/specialists
```

It supports create, edit, enable/disable, delete and reload.

Tool IDs are validated against the current registered Diagnostic Tool Registry;
unregistered IDs are rejected. The API does not grant arbitrary shell, SSH, or
SQL capability.

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
