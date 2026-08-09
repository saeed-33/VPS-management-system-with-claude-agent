# Knowledge RAG Contracts and Schema

**Phase:** 4.8.0
**Status:** Implemented — pending migration/runtime acceptance

Phase 4.8.0 introduces the durable document/chunk boundary:

```text
knowledge_sources
  -> knowledge_documents
      -> knowledge_chunks
```

A source can yield many documents (for example, a website with many pages).
A large PDF can be one document with hundreds of chunks. Retrieval later works
on the chunks, not on the whole file.

Document lifecycle:

```text
pending -> fetched -> parsed -> chunked -> indexed
                                   |
                                 failed
```

Chunks preserve section/page metadata and already reserve `search_vector` and
nullable `embedding vector(768)` fields. Full-text and HNSW indexes are deferred
to 4.8.3.

4.8.0 does not fetch URLs, parse PDFs/HTML, create chunks, calculate embeddings,
or retrieve context.
