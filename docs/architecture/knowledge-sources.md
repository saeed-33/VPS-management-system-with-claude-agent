# Knowledge Sources Foundation

**Phase:** 4.7  
**Status:** Implemented — pending migration/runtime acceptance

Phase 4.7 introduces user-managed knowledge source definitions.

```text
Operator
 -> /api/knowledge-sources
 -> KnowledgeSourceService
 -> KnowledgeSourceRepository
 -> knowledge_sources
 -> KnowledgeSourceRegistry
```

Supported source types:

```text
url
file
inline
```

A source can be scoped with:

```text
domains
specialist_slugs
tags
priority
enabled
```

Examples:

```text
Linux kernel scheduling documentation
domains = cpu, scheduler
specialist_slugs = linux-cpu

PostgreSQL performance guide
domains = postgresql, database, performance
specialist_slugs = postgresql
```

The Registry exposes enabled sources only and supports lookup by domain or
Specialist slug.

Phase 4.7 does not download URLs, upload files, parse documents, chunk
content, create embeddings, or perform semantic retrieval. Those belong to
Knowledge RAG in Phase 4.8.

## API

```text
GET    /api/knowledge-sources
GET    /api/knowledge-sources/{id}
POST   /api/knowledge-sources
PATCH  /api/knowledge-sources/{id}
PUT    /api/knowledge-sources/{id}/enabled
DELETE /api/knowledge-sources/{id}
```

## Migration

```powershell
psql -U <POSTGRES_USER> -d <POSTGRES_DB> `
  -f .\app\shared\database\migrations\step_4_7_knowledge_sources.sql
```

## Acceptance

```powershell
uv run python tools/bootstrap_database.py --verify-only
uv run python -m pytest
uv run python tools/list_routes.py
uv run python tools/inspect_knowledge_sources.py
```

After migration, database verification should report 13/13 tables.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
