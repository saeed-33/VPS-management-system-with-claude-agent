# Knowledge Embedding and Search Indexing

**Phase:** 4.8.3  
**Status:** Implemented — pending runtime acceptance

4.8.3 makes `knowledge_chunks` ready for lexical and semantic retrieval.

```text
knowledge_chunks
  -> generated search_vector -> GIN
  -> EmbeddingClient -> vector(768) -> HNSW cosine
```

Knowledge RAG reuses the same `EmbeddingClient` abstraction and embedding
settings used by Report RAG.

Each chunk stores:

```text
embedding
embedding_provider
embedding_model
embedding_dimensions
```

Once all chunks are processed, the parent document status becomes `indexed`.

Indexing is idempotent: embeddings are skipped when provider, model and
dimensions already match. `--force` regenerates them.

4.8.3 intentionally does not add the indexer to `ApplicationContainer`.
The command creates it from the existing KnowledgeDocumentRepository and the
shared embedding factory. Runtime retrieval wiring belongs to 4.8.4.

Apply indexes:

```powershell
psql -U <POSTGRES_USER> -d <POSTGRES_DB> `
  -f .\app\infrastructure\database\migrations\step_4_8_3_knowledge_indexes.sql
```

Then:

```powershell
uv run python tools/dev/index_knowledge_document.py 1
uv run python tools/dev/inspect_knowledge_index.py 1
```

Expected:

```text
Status: indexed
Chunks: 3
Embedded chunks: 3
Missing embeddings: 0
Search indexes: 2/2
Knowledge index acceptance: PASS
```

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
