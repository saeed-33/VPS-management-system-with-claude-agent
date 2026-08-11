# Documentation Inventory

<!-- DOC-STATUS: CURRENT -->

Generated: **2026-08-11**

Every Markdown document in `docs/` is classified below.

| Document | Classification | Title |
|---|---|---|
| [`docs/DOCUMENTATION_MAINTENANCE.md`](DOCUMENTATION_MAINTENANCE.md) | CURRENT | Documentation Maintenance |
| [`docs/PROJECT_STATUS.md`](PROJECT_STATUS.md) | CURRENT | Project Status |
| [`docs/PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) | CURRENT | Project Structure and File Responsibilities |
| [`docs/README.md`](README.md) | CURRENT | Project Documentation |
| [`docs/api/admin-management.md`](api/admin-management.md) | CURRENT | Admin Management Coverage |
| [`docs/api/admin-web-ui.md`](api/admin-web-ui.md) | CURRENT | Admin Web UI |
| [`docs/api/http-api.md`](api/http-api.md) | CURRENT | HTTP API Reference |
| [`docs/api/investigations.md`](api/investigations.md) | CURRENT | Investigation API |
| [`docs/api/specialists-api.md`](api/specialists-api.md) | CURRENT | Specialists Management API |
| [`docs/architecture/aggregate-production-readiness.md`](architecture/aggregate-production-readiness.md) | CURRENT | Aggregate Production Readiness — Phase 4.20.5 |
| [`docs/architecture/cross-specialist-correlation.md`](architecture/cross-specialist-correlation.md) | CURRENT | Cross-Specialist Correlation — Phase 4.18 |
| [`docs/architecture/database.md`](architecture/database.md) | CURRENT | Database Baseline |
| [`docs/architecture/diagnostic-policy.md`](architecture/diagnostic-policy.md) | CURRENT | Diagnostic Policy Engine |
| [`docs/architecture/diagnostic-tool-registry.md`](architecture/diagnostic-tool-registry.md) | CURRENT | Diagnostic Tool Registry |
| [`docs/architecture/dynamic-secondary-specialist-routing.md`](architecture/dynamic-secondary-specialist-routing.md) | CURRENT | Dynamic Secondary Specialist Routing — Phase 4.17 |
| [`docs/architecture/evaluation-dataset-runner.md`](architecture/evaluation-dataset-runner.md) | CURRENT | Evaluation Dataset & Deterministic Runner — Phase 4.20.2 |
| [`docs/architecture/evidence-collection.md`](architecture/evidence-collection.md) | CURRENT | Evidence Collection |
| [`docs/architecture/investigation-contracts.md`](architecture/investigation-contracts.md) | CURRENT | 4.1 — Investigation State and Multi-Agent Contracts |
| [`docs/architecture/investigation-persistence.md`](architecture/investigation-persistence.md) | CURRENT | Investigation Persistence |
| [`docs/architecture/investigation-read-models.md`](architecture/investigation-read-models.md) | CURRENT | Investigation Read Models — Phase 4.19.1 |
| [`docs/architecture/investigation-router.md`](architecture/investigation-router.md) | CURRENT | Investigation Router |
| [`docs/architecture/investigation-runtime-snapshot.md`](architecture/investigation-runtime-snapshot.md) | CURRENT | Runtime Snapshot Persistence — Phase 4.19.2 |
| [`docs/architecture/knowledge-chunking.md`](architecture/knowledge-chunking.md) | CURRENT | Structure-aware Knowledge Chunking |
| [`docs/architecture/knowledge-indexing.md`](architecture/knowledge-indexing.md) | CURRENT | Knowledge Embedding and Search Indexing |
| [`docs/architecture/knowledge-ingestion.md`](architecture/knowledge-ingestion.md) | CURRENT | Knowledge Ingestion and Parsing |
| [`docs/architecture/knowledge-rag-schema.md`](architecture/knowledge-rag-schema.md) | CURRENT | Knowledge RAG Contracts and Schema |
| [`docs/architecture/knowledge-retrieval.md`](architecture/knowledge-retrieval.md) | CURRENT | Knowledge Hybrid Retrieval and Reranking |
| [`docs/architecture/knowledge-sources-seed.md`](architecture/knowledge-sources-seed.md) | CURRENT | Knowledge Sources Seed and Acceptance |
| [`docs/architecture/knowledge-sources.md`](architecture/knowledge-sources.md) | CURRENT | Knowledge Sources Foundation |
| [`docs/architecture/langgraph-investigation-orchestration.md`](architecture/langgraph-investigation-orchestration.md) | CURRENT | LangGraph Investigation Orchestration |
| [`docs/architecture/overview.md`](architecture/overview.md) | CURRENT | Current Architecture |
| [`docs/architecture/persisted-runtime-evaluation.md`](architecture/persisted-runtime-evaluation.md) | CURRENT | Persisted Runtime Evaluation — Phase 4.20.3 |
| [`docs/architecture/production-readiness-gate.md`](architecture/production-readiness-gate.md) | CURRENT | Evaluation & Production Readiness Gate — Phase 4.20.1 |
| [`docs/architecture/runtime-sample-expansion.md`](architecture/runtime-sample-expansion.md) | CURRENT | Runtime Sample Expansion — Phase 4.20.6 |
| [`docs/architecture/safety-failure-injection.md`](architecture/safety-failure-injection.md) | CURRENT | Safety & Failure Injection — Phase 4.20.4 |
| [`docs/architecture/server-coordinator.md`](architecture/server-coordinator.md) | CURRENT | Server Coordinator — Phase 4.15 |
| [`docs/architecture/specialist-context-builder.md`](architecture/specialist-context-builder.md) | CURRENT | Specialist Context Builder |
| [`docs/architecture/specialist-definitions.md`](architecture/specialist-definitions.md) | CURRENT | Dynamic Specialist Definitions |
| [`docs/architecture/specialist-investigation-loop.md`](architecture/specialist-investigation-loop.md) | CURRENT | Specialist Investigation Loop |
| [`docs/architecture/specialist-reasoning-agent.md`](architecture/specialist-reasoning-agent.md) | CURRENT | Specialist Reasoning Agent |
| [`docs/architecture/specialist-registry.md`](architecture/specialist-registry.md) | CURRENT | Specialist Registry Service |
| [`docs/decisions/ADR-008-dynamic-specialists.md`](decisions/ADR-008-dynamic-specialists.md) | DECISION | ADR-008 — Specialists Are User-Defined Runtime Data |
| [`docs/decisions/ADR-009-hierarchical-investigation.md`](decisions/ADR-009-hierarchical-investigation.md) | DECISION | ADR-009 — Hierarchical, Bounded, Read-Only Investigation |
| [`docs/decisions/ADR-010-langgraph-orchestration-boundary.md`](decisions/ADR-010-langgraph-orchestration-boundary.md) | DECISION | ADR-010 — LangGraph Orchestration Boundary |
| [`docs/decisions/ADR-011-dual-rag-and-knowledge-retrieval.md`](decisions/ADR-011-dual-rag-and-knowledge-retrieval.md) | DECISION | ADR-011 — Separate Incident RAG and Knowledge RAG with Hybrid Retrieval |
| [`docs/decisions/ADR-012-specialist-reasoning-and-provenance-boundary.md`](decisions/ADR-012-specialist-reasoning-and-provenance-boundary.md) | DECISION | ADR-012 — Specialist Reasoning Is Structured, Read-Only, and Provenance-Gated |
| [`docs/decisions/ADR-013-registered-read-only-diagnostic-tools.md`](decisions/ADR-013-registered-read-only-diagnostic-tools.md) | DECISION | ADR-013 — Specialists Use Registered Read-Only Diagnostic Tools, Never Arbitrary Shell |
| [`docs/decisions/ADR-014-langgraph-investigation-orchestration.md`](decisions/ADR-014-langgraph-investigation-orchestration.md) | DECISION | ADR-014: LangGraph for Investigation Orchestration |
| [`docs/decisions/ADR-015-dynamic-secondary-specialist-routing.md`](decisions/ADR-015-dynamic-secondary-specialist-routing.md) | DECISION | ADR-015: Dynamic Secondary Specialist Routing |
| [`docs/decisions/ADR-016-production-readiness-and-remediation-boundary.md`](decisions/ADR-016-production-readiness-and-remediation-boundary.md) | DECISION | ADR-016 — Production Readiness Gate and Remediation Boundary |
| [`docs/decisions/README.md`](decisions/README.md) | REFERENCE | Architecture Decision Records |
| [`docs/deployment/production-checklist.md`](deployment/production-checklist.md) | CURRENT | Production / Supervised Operations Checklist |
| [`docs/deployment/production-deployment.md`](deployment/production-deployment.md) | CURRENT | Production Deployment Baseline |
| [`docs/deployment/systemd-example.md`](deployment/systemd-example.md) | CURRENT | systemd Example |
| [`docs/operations/configuration.md`](operations/configuration.md) | CURRENT | Configuration Reference |
| [`docs/operations/database-bootstrap.md`](operations/database-bootstrap.md) | CURRENT | Database Bootstrap |
| [`docs/operations/migrations-and-troubleshooting.md`](operations/migrations-and-troubleshooting.md) | CURRENT | Migrations and Troubleshooting |
| [`docs/operations/running-project.md`](operations/running-project.md) | CURRENT | Running the Project |
| [`docs/rag_configuration.md`](rag_configuration.md) | REFERENCE | RAG Configuration Policy |
| [`docs/roadmap/next-phase-multi-agent.md`](roadmap/next-phase-multi-agent.md) | CURRENT | Next Phase — Supervised Remediation |
| [`docs/roadmap/phase-4-17-closeout.md`](roadmap/phase-4-17-closeout.md) | HISTORICAL | Phase 4.17 Closeout — Dynamic Secondary Specialist Routing |
| [`docs/roadmap/phase-4-18-implementation.md`](roadmap/phase-4-18-implementation.md) | HISTORICAL | Phase 4.18 Implementation Notes |
| [`docs/roadmap/phase-4-19-implementation.md`](roadmap/phase-4-19-implementation.md) | HISTORICAL | Phase 4.19 Implementation Notes |
| [`docs/roadmap/phase-4-20-closeout.md`](roadmap/phase-4-20-closeout.md) | CURRENT | Phase 4.20 Closeout |
| [`docs/roadmap/phase-4-20-implementation.md`](roadmap/phase-4-20-implementation.md) | CURRENT | Phase 4.20 — Evaluation, Safety & Production Readiness |
| [`docs/roadmap/phase-4-4-5-to-4-11-closeout.md`](roadmap/phase-4-4-5-to-4-11-closeout.md) | HISTORICAL | Phase 4 Closeout — Steps 4.5 through 4.11 |
| [`docs/roadmap/phase-4-foundation-closeout.md`](roadmap/phase-4-foundation-closeout.md) | HISTORICAL | Phase 4 Milestone A Closeout — Foundation |
| [`docs/roadmap/phase-4-implementation-plan.md`](roadmap/phase-4-implementation-plan.md) | CURRENT | Phase 4 Implementation Plan — Hierarchical Multi-Agent Investigation |
| [`docs/security/security-baseline.md`](security/security-baseline.md) | CURRENT | Security Baseline |
| [`docs/testing/RUNTIME_SCENARIOS.md`](testing/RUNTIME_SCENARIOS.md) | CURRENT | Linux Random Runtime Scenarios |
| [`docs/testing/TESTING_STRATEGY.md`](testing/TESTING_STRATEGY.md) | CURRENT | Testing Strategy |
| [`docs/testing/TEST_CATALOG.md`](testing/TEST_CATALOG.md) | CURRENT | Complete Test Catalog |
| [`docs/testing/multi-agent-test-methodology.md`](testing/multi-agent-test-methodology.md) | CURRENT | منهجية الاختبارات — Multi-Agent Investigation |
| [`docs/testing/performance.md`](testing/performance.md) | REFERENCE | Performance Baseline |
| [`docs/testing/testing-and-evaluation.md`](testing/testing-and-evaluation.md) | CURRENT | Testing and Evaluation |
| [`docs/ui/investigations.md`](ui/investigations.md) | CURRENT | Investigation Administration UI |
| [`docs/workflows/current-workflows.md`](workflows/current-workflows.md) | CURRENT | Current Workflows |

## Classification meanings

- **CURRENT** — active description/instructions for the current system.
- **HISTORICAL** — preserved implementation/closeout history; body may intentionally mention earlier phases.
- **DECISION** — accepted ADR; preserved as a decision record.
- **REFERENCE** — supporting reference material.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
