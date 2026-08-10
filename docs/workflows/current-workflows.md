# Current Workflows

## Monitoring

```text
Load server
 -> validate monitor_enabled/profile
 -> load enabled commands
 -> SSH
 -> execute commands
 -> build/save report
 -> enqueue analysis
```

## Initial Report Analysis

```text
Report
 -> normalize + fingerprint
 -> exact match? -> REUSE
 -> otherwise Incident Hybrid Retrieval
 -> accepted context? -> ASSISTED
 -> none? -> FULL
 -> LLM for ASSISTED/FULL
 -> save/index/metrics
```

Exact fingerprint reuse and semantic retrieval remain different mechanisms.

## Investigation Routing

```text
Monitoring Report
+
Initial Analysis
+
SpecialistRegistrySnapshot
 -> actionable signal?
 -> detect domains
 -> candidate Specialists
 -> ranked baseline selection
 -> InvestigationRoutingDecision
```

Healthy reports do not open investigations merely because Specialists exist.

Connection failures are classified toward network/connectivity rather than
generic process routing.

## Investigation Persistence

```text
Routing Decision
 -> Investigation
 -> Candidate Specialist records
 -> Selected Specialist records
 -> database
 -> reload/inspect
```

## Knowledge Source Lifecycle

```text
Operator-defined Knowledge Source
 -> enabled/disabled metadata
 -> loader
 -> parser
 -> KnowledgeDocument(parsed)
 -> structure-aware chunker
 -> KnowledgeChunk
 -> embeddings + FTS
 -> KnowledgeDocument(indexed)
```

## Knowledge Search

```text
Specialist problem/query
   +--> Vector Search / HNSW
   +--> Full-Text Search / GIN
                |
                v
             RRF fusion
                |
                v
    Specialist/domain scope reranking
                |
                v
        attributed Top-K chunks
```

Search is restricted to enabled sources and indexed documents.

The current baseline uses deterministic reranking; no LLM reranker is required.

## Specialist Context

```text
SpecialistTask
+ Specialist Instructions
+ Initial Analysis
+ selected current Evidence
+ Incident RAG
+ Knowledge RAG
 -> SpecialistContextBuilder
 -> context budgets
 -> provenance markers
 -> SpecialistContextSnapshot
```

Markers include:

```text
[evidence:<id>]
[incident:report-<id>/analysis-<id>]
[knowledge:chunk-<id>]
```

## Specialist Reasoning

```text
SpecialistContextSnapshot
 -> SpecialistReasoningClient
 -> strict Pydantic output
 -> evidence/knowledge ID validation
 -> SpecialistResult
```

Current reasoning is read-only and has no Tool Request schema.

When evidence is insufficient, the expected output is low confidence plus
`missing_evidence`, not fabricated operational facts.

## Diagnostic Tool Definition

```text
Specialist allowed_tool_ids
 -> DiagnosticToolRegistry
 -> tool exists?
 -> typed parameters valid?
 -> fixed safe command rendering
```

At Phase 4.11 this workflow stops before SSH execution.

No arbitrary shell path exists.

## Next workflow boundary — 4.12/4.13

```text
Specialist requests Tool
 -> Diagnostic Policy Engine
 -> allow / deny
 -> approved registered Tool
 -> existing bounded SSH implementation
 -> execution result
 -> Evidence
 -> next Specialist reasoning round
```

Policy and Evidence Collection remain separate responsibilities.
