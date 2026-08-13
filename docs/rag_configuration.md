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

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution see `docs/testing/TESTING_STRATEGY.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

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
