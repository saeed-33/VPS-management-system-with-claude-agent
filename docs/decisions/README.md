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

## ADR-010 — Superseded orchestration boundary
**Superseded for future orchestration by ADR-017.** Registry/RAG/database/policy/tools/SSH remain project-owned Python services, while Claude Code owns high-level supervisory orchestration going forward.

## ADR-011 — Separate Incident RAG and Knowledge RAG with Hybrid Retrieval
**Accepted.** Incident history and technical documentation remain separate retrieval systems. Knowledge RAG uses structure-aware chunks, PostgreSQL FTS, pgvector/HNSW, RRF fusion, Specialist/domain scope, deterministic reranking, and preserved source attribution. See `ADR-011-dual-rag-and-knowledge-retrieval.md`.

## ADR-012 — Specialist reasoning and provenance boundary
**Accepted.** Specialist LLM reasoning is structured and read-only; Evidence and Knowledge IDs are validated against the actual context, documentation is not proof of server state, and missing evidence is first-class output. See `ADR-012-specialist-reasoning-and-provenance-boundary.md`.

## ADR-013 — Registered read-only diagnostic tools
**Accepted.** Specialists choose from finite registered capabilities through `allowed_tool_ids`; typed parameters and fixed command templates prevent arbitrary shell. SSH execution remains behind policy/evidence stages. See `ADR-013-registered-read-only-diagnostic-tools.md`.

- [ADR-015: Dynamic Secondary Specialist Routing](ADR-015-dynamic-secondary-specialist-routing.md)
- [ADR-016: Production Readiness and Remediation Boundary](ADR-016-production-readiness-and-remediation-boundary.md)
- [ADR-017: Claude Code as Supervisory Agent Runtime](ADR-017-claude-code-supervisory-agent-runtime.md)
- [ADR-018: Claude-Native Operational Contracts](ADR-018-claude-native-operational-contracts.md)

## Claude runtime decisions

ADR-017 accepts Claude Code as the supervisory orchestration runtime.

ADR-018 clarifies the operational meaning of that decision:

```text
Claude reasoning/orchestration
 -> operational skills and bounded agents
 -> project MCP tools
 -> Python execution/policy/persistence
```

Commands are not maintained as a duplicate workflow surface. Global rules are
limited to cross-workflow invariants. Hooks are introduced only when they
enforce or audit a concrete runtime condition.

Dynamic Specialists remain DB-defined. Python remains authoritative for
execution, policy, evidence, RAG, SSH, persistence, and remediation
authorization.

Phase 5 remains blocked until C.14 proves a real Ollama-backed Claude execution
path and re-passes the runtime safety/readiness gate.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
