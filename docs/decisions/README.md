# Architecture Decision Records

## ADR-001 — Canonical normalization
**Accepted.** يتم تطبيع line endings/whitespace/ANSI/timestamps وترتيب executions قبل fingerprint. الهدف تقليل cache misses غير الدلالية. `command_set_hash` جزء من scope.

## ADR-002 — Exact fingerprint only for REUSE
**Accepted.**
```text
Exact fingerprint -> REUSE
Semantic similarity -> context only
```
لا يوجد semantic reuse في baseline.

## ADR-003 — pgvector semantic retrieval
**Accepted.** embeddings + cosine similarity تستخدم لاسترجاع الحالات الدلالية مع minimum similarity ونطاق retrieval.

## ADR-004 — Hybrid retrieval with RRF
**Accepted.** Vector وFTS يدمجان بالرتب لأن درجاتهما الخام غير متجانسة. RRF لا يمثل نسبة تشابه.

## ADR-005 — Structured Compatibility
**Accepted.** similarity وحدها غير كافية. تعارض connection/command success/exit status يمكن أن يرفض candidate عالي similarity.

## ADR-006 — HNSW
**Accepted.** HNSW هو ANN index الحالي للـvector، و`RAG_HNSW_EF_SEARCH` يضبط search effort.

## ADR-007 — Semantic gate before assisted context
**Accepted.** Full-Text لا يستطيع وحده إدخال candidate إلى LLM. المرشح يجب أن يجتاز `RAG_MINIMUM_SIMILARITY` عبر vector score.

## Consequence for UI
تعرض الواجهة `vector_score` عند إظهار similarity. لا تعرض RRF كنسبة مئوية.
