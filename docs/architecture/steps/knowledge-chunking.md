# Structure-aware Knowledge Chunking

**Phase:** 4.8.2  
**Status:** Implemented — pending runtime acceptance

4.8.2 converts parsed documents into durable retrieval units:

```text
knowledge_documents(status=parsed)
        |
StructureAwareKnowledgeChunker
        |
KnowledgeChunkDraft[]
        |
knowledge_chunks
        |
knowledge_documents(status=chunked)
```

Default budget:

```text
target_chars  = 1800
max_chars     = 2600
overlap_chars = 240
min_chars     = 180
```

The chunker prefers paragraph boundaries. Oversized paragraphs are split by
sentence boundary before a hard size cut is used.

HTML parsing now records heading text and PDF parsing records text per page.
This lets chunks preserve `section_title` and `page_number` where the source
structure supports it.

Already parsed documents remain compatible through paragraph-aware fallback,
but re-ingesting them after 4.8.2 enriches their structure metadata.

Chunking is idempotent for a document: rerunning it replaces prior chunks and
sets document status to `chunked`.

Embeddings remain NULL. Phase 4.8.3 performs indexing.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

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
