# Project Documentation

هذه الوثائق تصف baseline التنفيذ الحالي للمشروع حتى إغلاق Phase 4.17 runtime acceptance.

## Current implementation status

- Milestone A — Foundation (4.0–4.4): COMPLETED
- Milestone B — Routing + Knowledge (4.5–4.9): COMPLETED
- Milestone C — Single Specialist Investigation (4.10–4.14): COMPLETED
- Milestone D:
  - 4.15 Server Coordinator: COMPLETED
  - 4.16 LangGraph Parallel Investigation: COMPLETED
  - 4.17 Dynamic Secondary Specialist Routing: COMPLETED
  - 4.18 Correlation + Final Diagnosis: NEXT
- Milestone E — Productization (4.19–4.20): PLANNED

Reference automated baseline after the latest accepted 4.17 work:

```text
184 passed, 1 warning
```

The warning is the existing Starlette/TestClient deprecation warning and is not a Phase 4.17 functional failure.

## Architecture

- [Architecture Overview](architecture/overview.md)
- [Investigation Contracts](architecture/investigation-contracts.md)
- [Investigation Router](architecture/investigation-router.md)
- [Investigation Persistence](architecture/investigation-persistence.md)
- [Specialist Registry](architecture/specialist-registry.md)
- [Specialist Context Builder](architecture/specialist-context-builder.md)
- [Specialist Reasoning Agent](architecture/specialist-reasoning-agent.md)
- [Diagnostic Tool Registry](architecture/diagnostic-tool-registry.md)
- [Diagnostic Policy Engine](architecture/diagnostic-policy.md)
- [Evidence Collection](architecture/evidence-collection.md)
- [Specialist Investigation Loop](architecture/specialist-investigation-loop.md)
- [Server Coordinator](architecture/server-coordinator.md)
- [LangGraph Investigation Orchestration](architecture/langgraph-investigation-orchestration.md)
- [Dynamic Secondary Specialist Routing](architecture/dynamic-secondary-specialist-routing.md)
- [Knowledge Sources](architecture/knowledge-sources.md)
- [Knowledge Retrieval](architecture/knowledge-retrieval.md)

## Workflows and testing

- [Current Workflows](workflows/current-workflows.md)
- [Multi-Agent Test Methodology](testing/multi-agent-test-methodology.md)
- [Testing and Evaluation](testing/testing-and-evaluation.md)
- [Performance](testing/performance.md)

## Decisions

- [Architecture Decisions](decisions/README.md)
- [ADR-008: Dynamic Specialists](decisions/ADR-008-dynamic-specialists.md)
- [ADR-009: Hierarchical Investigation](decisions/ADR-009-hierarchical-investigation.md)
- [ADR-010: LangGraph Orchestration Boundary](decisions/ADR-010-langgraph-orchestration-boundary.md)
- [ADR-011: Dual RAG and Knowledge Retrieval](decisions/ADR-011-dual-rag-and-knowledge-retrieval.md)
- [ADR-012: Specialist Reasoning and Provenance](decisions/ADR-012-specialist-reasoning-and-provenance-boundary.md)
- [ADR-013: Registered Read-Only Diagnostic Tools](decisions/ADR-013-registered-read-only-diagnostic-tools.md)
- [ADR-014: LangGraph Investigation Orchestration](decisions/ADR-014-langgraph-investigation-orchestration.md)
- [ADR-015: Dynamic Secondary Specialist Routing](decisions/ADR-015-dynamic-secondary-specialist-routing.md)

## Roadmap

- [Phase 4 Implementation Plan](roadmap/phase-4-implementation-plan.md)
- [Phase 4.17 Closeout](roadmap/phase-4-17-closeout.md)

قاعدة التوثيق: كل ملف خارج `roadmap/` يجب أن يصف التنفيذ الحالي الفعلي، لا التصميم المستقبلي المفترض.
