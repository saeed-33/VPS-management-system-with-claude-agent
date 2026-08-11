# Knowledge Hybrid Retrieval and Reranking

**Phase:** 4.8.4
**Status:** Implemented — pending runtime acceptance

4.8.4 retrieves small relevant Knowledge Chunks instead of passing a whole
source document to a Specialist.

```text
Specialist query
      |
      +--> Vector search (HNSW)
      |
      +--> Full-text search (GIN)
      |
      +--> RRF fusion
      |
      +--> deterministic scope reranking
      |
      +--> Top-K chunks
```

Search includes enabled sources and indexed documents only.

When Specialist/domain scope is provided, sources are eligible when they match
the Specialist OR at least one requested domain.

RRF merges vector and lexical ranks by chunk ID. A small deterministic rerank
boost is then applied for direct Specialist scope, domain overlap and source
priority. No LLM reranker is used in this phase.

Acceptance:

```powershell
uv run python tools/search_knowledge.py `
  "nginx modules configuration" `
  --specialist nginx `
  --domains nginx,http,proxy
```

The current NGINX seed contains only the documentation index page. Detailed
directive retrieval will improve when multi-page website crawling is added.

Phase 4.8.5 injects retrieved chunks into Specialist context.

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
