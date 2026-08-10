# Current Architecture

## Implemented baseline through Phase 4.11

```text
Admin / Web
   |
Shared Services / Repositories
   |
MonitoringScheduler
   |
MonitoringService
   |
SSH
   |
Monitoring Report
   |
AnalysisAgentManager
   |
AnalysisOrchestrator
   +--> ReportNormalizer / Fingerprint
   +--> AnalysisReusePolicy
   +--> Incident HybridRetriever
   +--> RagContextBuilder
   +--> ReportAnalyzer / LLM
   +--> RetrievalIndexer
   |
PostgreSQL + pgvector

Phase 4 Investigation
   |
InvestigationRouter
   |
Investigation Persistence
   |
SpecialistRegistry
   |
Selected Dynamic Specialist
   |
SpecialistContextBuilder
   +--> Initial Analysis
   +--> Current Evidence
   +--> Incident RAG
   +--> Knowledge RAG
   +--> Specialist Instructions
   |
SpecialistReasoningAgent
   |
Structured SpecialistResult
   |
DiagnosticToolRegistry
```

## Dynamic Specialists

Specialists are persisted operator-managed data, not hard-coded Python agent
classes.

Runtime definitions include:

```text
slug/name
instructions
domains
trigger hints
knowledge topics
allowed_tool_ids
priority
max rounds
max actions
```

The Specialist Registry exposes enabled validated definitions and stable
snapshots for routing.

## Investigation routing

The Router is deterministic and conservative before LLM reasoning.

It decides:

```text
should investigate?
detected domains
candidate Specialists
selected Specialists
unmatched issues
```

The candidate pool is intentionally larger than the final selection pool so a
later ranking/selection mechanism has enough options without invoking every
Specialist.

## Two RAG systems

### Incident RAG

Purpose:

```text
retrieve similar historical monitoring incidents/analyses
```

It is used as historical context, not exact truth for the current server.

### Knowledge RAG

Purpose:

```text
retrieve small relevant technical-documentation chunks
```

Pipeline:

```text
Knowledge Sources
 -> load/parse
 -> structure-aware chunking
 -> PostgreSQL search_vector + GIN
 -> embeddings vector(768) + HNSW
 -> vector + full-text retrieval
 -> RRF
 -> Specialist/domain reranking
 -> Top-K attributed chunks
```

Incident RAG and Knowledge RAG are deliberately separate.

See ADR-011.

## Specialist Context Builder

The Context Builder creates a bounded Specialist-specific snapshot from:

```text
SpecialistTask
Specialist instructions
initial analysis
selected current evidence
Incident RAG
Knowledge RAG
```

Current default total context limit:

```text
18000 characters
```

Every source retains a stable provenance ID.

## Specialist Reasoning

Phase 4.10 is LLM reasoning-only.

Output is strict structured data:

```text
summary
confidence
findings
hypotheses
ruled_out
missing_evidence
recommended_next_specialists
```

Evidence/Knowledge IDs returned by the model are validated against the actual
context before conversion to `SpecialistResult`.

Technical documentation is not accepted as proof of live server state.

See ADR-012.

## Diagnostic Tool Registry

Phase 4.11 defines a finite set of registered read-only diagnostic
capabilities.

The LLM is never given arbitrary shell.

A Tool owns:

```text
typed parameters
fixed command template
timeout
output limit
risk metadata
```

Specialist definitions own the permission list through `allowed_tool_ids`.

4.11 defines Tools only; it does not execute them yet.

See ADR-013.

## Composition and orchestration boundary

`app/bootstrap.py` remains the composition root.

LangGraph is still not required for the implemented services. ADR-010 reserves
it for later stateful orchestration when the investigation loop/coordinator
benefits from graph execution.

Project-owned services remain responsible for:

```text
database/repositories
RAG
registry
policy
diagnostic tools
SSH
```

## Not implemented yet

```text
4.12 Diagnostic Policy Engine
4.13 Evidence Collection
4.14 Specialist Investigation Loop
4.15 Server Coordinator
4.16 Parallel Investigation
4.17 Dynamic Secondary Specialists
4.18 Correlation + Final Diagnosis
4.19 Investigation API/UI
4.20 Evaluation & Safety Gate
```

Autonomous remediation remains explicitly outside Phase 4.
