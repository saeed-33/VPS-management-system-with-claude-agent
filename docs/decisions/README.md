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

## ADR-008 — Dynamic user-defined specialists
**Accepted.** Specialist definitions are persisted user-managed data; the application provides a generic engine/registry/policy rather than hard-coded specialist classes. See `ADR-008-dynamic-specialists.md`.

## ADR-009 — Hierarchical bounded read-only investigation
**Accepted.** Server Coordinator + dynamic Specialists operate within specialist/round/action budgets. Phase 4 permits registered read-only diagnostics only; remediation is deferred to Phase 5. See `ADR-009-hierarchical-investigation.md`.

## ADR-010 — LangGraph orchestration boundary
**Accepted.** LangGraph is reserved for later stateful investigation orchestration. Registry/RAG/database/policy/tools/SSH remain project-owned Python services. See `ADR-010-langgraph-orchestration-boundary.md`.

