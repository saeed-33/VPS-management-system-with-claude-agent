# Current Architecture

## Implemented baseline through Phase 4.17

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
Selected Dynamic Specialists
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
Diagnostic Tool Requests
   |
DiagnosticToolRegistry
   |
DiagnosticPolicyEngine
   |
EvidenceCollectionService
   |
Known read-only SSH implementations
   |
SpecialistInvestigationLoop
   |
Server Coordinator
   |
LangGraph parallel Specialist wave
   |
Dynamic secondary Specialist routing
   |
Accumulated SpecialistResults + Evidence
```

## Dynamic Specialists

Specialists are persisted operator-managed data, not hard-coded Python agent classes.

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

The Specialist Registry exposes enabled validated definitions and stable snapshots for routing.

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

Healthy reports do not open investigations merely because Specialists exist.

## Two RAG systems

### Incident RAG

Purpose:

```text
retrieve similar historical monitoring incidents/analyses
```

Historical incidents are context, not proof of current server state.

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

Incident RAG and Knowledge RAG remain separate by design.

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

Every Evidence/Knowledge source retains a stable provenance ID.

## Specialist Reasoning

Normal reasoning returns strict structured data:

```text
summary
confidence
findings
hypotheses
ruled_out
missing_evidence
recommended_next_specialists
diagnostic_tool_requests
```

Evidence/Knowledge IDs emitted by the model are validated against the actual context. Technical documentation is not accepted as proof of live server state.

Final Synthesis uses a smaller provider-level contract:

```text
summary
confidence
missing_evidence
recommended_next_specialists
```

This reduces malformed/truncated JSON risk after Tool execution has ended.

## Diagnostic execution boundary

The LLM never receives arbitrary shell capability.

```text
LLM structured Tool request
 -> Diagnostic Tool Registry
 -> Diagnostic Policy Engine
 -> typed parameter validation
 -> approved execution envelope
 -> Evidence Collection
 -> known read-only SSH command
 -> EvidenceReference
```

Only approved executions consume action budget.

## Specialist Investigation Loop

Each Specialist operates inside bounded rounds/actions.

```text
reason
 -> optional Tool request
 -> policy
 -> evidence
 -> rebuild context
 -> reason again
 -> final synthesis
```

Duplicate Tool requests are suppressed and do not consume another action.

## Server Coordinator and LangGraph

Phase 4.15 introduced the server-level Coordinator.

Phase 4.16 moved independent Specialist execution to a bounded LangGraph parallel wave with deterministic per-worker action quotas.

Phase 4.17 adds sequential follow-up waves based on `recommended_next_specialists`.

A secondary recommendation is executable only when:

```text
slug exists in enabled Registry
not already executed
specialist budget remains
global action budget remains
```

Recommendations are advisory; the model cannot fabricate an executable Specialist.

LangGraph owns workflow orchestration only. Project-owned services remain responsible for:

```text
database/repositories
Incident RAG
Knowledge RAG
Specialist Registry
Diagnostic Tool Registry
Diagnostic Policy
Evidence Collection
SSH execution
domain contracts
```

## Runtime acceptance baseline

Phase 4.17 controlled runtime acceptance proved:

```text
Initial Specialist:    nginx
Secondary Specialist:  systemd-service
Waves completed:       2
Actions used:          3/10
Execution mode:        dynamic-secondary
```

Reference automated regression baseline:

```text
184 passed, 1 warning
```

## Current boundary

Implemented through **Phase 4.17**.

Not implemented yet:

```text
4.18 Correlation + Final Diagnosis
4.19 Investigation API/UI
4.20 Evaluation & Safety Gate
```

Phase 4.18 must correlate multiple Specialist results and Evidence into server-level claims classified as:

```text
confirmed
probable
unknown
```

Every material diagnosis claim must remain traceable to Evidence and/or explicitly attributed technical Knowledge. Conflicting Specialist conclusions must remain visible.

Autonomous remediation remains explicitly outside Phase 4.
