# ADR-011 — Separate Incident RAG and Knowledge RAG with Hybrid Retrieval

**Status:** Accepted  
**Phase:** 4.8–4.9

## Decision

The project uses two distinct retrieval systems with different semantics:

```text
Incident RAG
    historical monitoring reports / analyses
    -> "Have we seen a similar incident before?"

Knowledge RAG
    official/internal/external technical documentation
    -> "What technical knowledge is relevant to this problem?"
```

They must not be collapsed into one corpus or one trust model.

## Knowledge ingestion pipeline

Knowledge Sources are operator-managed metadata records. Enabled sources flow
through:

```text
Knowledge Source
    -> loader
    -> parser
    -> KnowledgeDocument
    -> structure-aware chunker
    -> KnowledgeChunk
    -> embedding + search_vector
    -> indexes
```

The current embedding backend reuses the same project-owned
`EmbeddingClient` abstraction used by Report RAG.

The current embedding dimensions are:

```text
768
```

The accepted runtime model during 4.8 acceptance was:

```text
ollama / nomic-embed-text
```

## Structure-aware chunking

Documents are not sent whole to the LLM.

Default chunking targets are approximately:

```text
target_chars   1800
max_chars      2600
overlap_chars   240
min_chars       180
```

Structural boundaries are preferred over blind fixed-width splitting:

```text
section/paragraph boundary
    >
sentence boundary
    >
hard split as fallback
```

HTML section titles and PDF page numbers are retained when available.

## Search indexes

Knowledge chunks use both lexical and semantic indexing:

```text
search_vector
    -> PostgreSQL GIN

embedding vector(768)
    -> pgvector HNSW cosine
```

## Hybrid retrieval

A Specialist knowledge query is searched through two independent branches:

```text
Query
  +--> Vector / HNSW
  +--> Full-Text / GIN
              |
              v
           RRF fusion
              |
              v
    deterministic scope reranking
              |
              v
           Top-K chunks
```

### Why RRF

Vector similarity and PostgreSQL FTS rank are not numerically comparable.
Raw scores must therefore not be averaged as though they shared a common
scale.

Reciprocal Rank Fusion combines **rank positions**, not raw scores.

This is consistent with ADR-004 for Incident RAG.

## Scope filtering

Knowledge retrieval only considers:

```text
knowledge_sources.enabled = true
knowledge_documents.status = indexed
```

When Specialist/domain scope exists, a source is eligible when it matches:

```text
specialist_slugs contains specialist
OR
domains contains one or more requested domains
```

The final deterministic rerank can apply small explainable boosts for:

```text
direct Specialist match
domain overlap
source priority
```

An LLM reranker is deliberately not part of the current baseline.

## Attribution

Every returned Knowledge Chunk retains:

```text
chunk_id
document_id
source_id
source_slug
canonical_uri
section_title
page_number
retrieval strategy
fusion/vector/text scores
```

The Specialist Context Builder converts retrieved chunks into traceable
`KnowledgeSourceReference` records.

## Important limitation discovered during acceptance

The current NGINX seed URL points to the documentation index page only.

Hybrid retrieval worked correctly, but some returned chunks contained module
lists or navigation content instead of the detailed directive documentation.

Therefore:

```text
retrieval correctness != corpus quality
```

Multi-page website discovery/crawling is a future ingestion enhancement.
The retrieval architecture does not require redesign to add it.

## Consequences

- Incident history and technical documentation retain different meanings.
- Whole 100-page documents are never injected blindly into a prompt.
- Search is explainable and independently testable.
- Source provenance survives into Specialist reasoning.
- Corpus quality must be evaluated separately from retrieval mechanics.
