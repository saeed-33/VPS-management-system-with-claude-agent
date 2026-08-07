# RAG Configuration Policy

## Core switches

- RAG_EXACT_REUSE_ENABLED=true
- RAG_ASSISTED_ENABLED=true
- RAG_VECTOR_ENABLED=true
- RAG_FULL_TEXT_ENABLED=true
- RAG_STRUCTURED_COMPATIBILITY_ENABLED=true

## Thresholds

- RAG_MINIMUM_SIMILARITY=0.72
- RAG_TOP_K=5
- RAG_CONTEXT_TOP_K=3
- RAG_FULL_TEXT_CANDIDATE_LIMIT=20
- RAG_FULL_TEXT_MINIMUM_RANK=0.0
- RAG_RRF_K=60

## Invariants

1. Assisted retrieval requires vector retrieval.
2. Full-text retrieval currently depends on the same retrieval-document indexing pipeline, so it also requires vector indexing.
3. RAG_CONTEXT_TOP_K must not exceed RAG_TOP_K.
4. Exact fingerprint reuse is independent from semantic similarity.
5. RRF is ranking-only and must never be displayed as semantic similarity.
