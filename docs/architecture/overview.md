# Current Architecture

## Current implemented baseline

```text
Admin / Web
   |
Shared Services / Repositories
   |
MonitoringScheduler -> MonitoringService -> SSH
   |
Monitoring Report
   |
AnalysisAgentManager
   |
AnalysisOrchestrator
   +--> ReportNormalizer / Fingerprint
   +--> AnalysisReusePolicy
   +--> HybridRetriever
   +--> RagContextBuilder
   +--> ReportAnalyzer / LLM
   +--> RetrievalIndexer
   |
PostgreSQL + pgvector

Phase 4 Foundation
   |
SpecialistDefinitionRepository
   |
SpecialistDefinitionService
   |
SpecialistRegistry
   |
SpecialistRegistrySnapshot
```

## Current responsibilities

- Monitoring collects server state.
- Analysis produces REUSE / ASSISTED / FULL analysis.
- Incident RAG retrieves historical report analyses.
- `app/bootstrap.py` is the composition root.
- Specialist definitions are user-managed persisted data.
- Specialist Registry converts enabled definitions into validated immutable runtime definitions.
- Registry Snapshot provides one coherent Specialist set for one future routing decision.

## Phase 4 Foundation completed

Milestone A (4.0–4.4) is complete. The runtime can create/edit/enable/disable/delete Specialist definitions, persist them, load enabled definitions only, validate them, normalize domains, create a stable snapshot, and perform deterministic domain lookup.

## Not implemented yet

Investigation Router, investigation persistence, Knowledge Sources/RAG, Specialist Context Builder, Specialist LLM reasoning, Tool Registry, Policy Engine, Specialist evidence collection, iterative investigation loops, Server Coordinator, parallel investigation, dynamic secondary specialists, final correlation/diagnosis, and Investigation UI.

LangGraph is not currently part of runtime execution. ADR-010 reserves it for later stateful orchestration only.
