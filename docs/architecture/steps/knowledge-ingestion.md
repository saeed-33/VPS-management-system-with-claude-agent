# Knowledge Ingestion and Parsing

**Phase:** 4.8.1  
**Status:** Implemented — pending runtime acceptance

4.8.1 implements the first real Knowledge RAG ingestion pipeline:

```text
knowledge_source
  -> KnowledgeSourceLoader
  -> KnowledgeContentParser
  -> ParsedKnowledgeDocument
  -> KnowledgeDocumentRepository
  -> knowledge_documents
```

Supported source types:

```text
inline
file
url
```

Supported content in this step:

```text
plain text / Markdown
HTML
PDF
```

URL ingestion intentionally fetches one URL only. Multi-page website crawling
is not enabled yet. This prevents an operator-configured documentation root
from unexpectedly crawling thousands of pages without crawl scope and budget.

PDF parsing uses `pypdf`. HTML parsing uses Python's standard `html.parser`.

The parsed text is temporarily persisted in `knowledge_documents.metadata`
under `parsed_text`. This is an intermediate 4.8.1 representation. In 4.8.2,
structure-aware chunks become the durable retrieval units; after chunk
materialization, retaining the full parsed text can be revisited.

Runtime acceptance example:

```powershell
uv run python tools/dev/ingest_knowledge_source.py nginx-docs
```

Expected document status:

```text
parsed
```

4.8.1 does not create chunks, embeddings, FTS indexes, HNSW indexes, or
retrieve context.

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
