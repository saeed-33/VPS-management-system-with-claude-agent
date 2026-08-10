# Phase 4 Closeout — Steps 4.5 through 4.11

**Status:** Completed and runtime-verified  
**Next:** 4.12 — Diagnostic Policy Engine

## Completed capabilities

### 4.5 — Investigation Router

The Router determines whether an investigation is required, detects domains,
builds a larger candidate set, and selects enabled dynamic Specialists.

Healthy report acceptance:

```text
report 825
should investigate: false
reason: no_actionable_signal
selected specialists: 0
```

Connection failure acceptance:

```text
report 807
detected domains: connectivity, network
selected: linux-network
```

The routing fix prevented a connection failure from being misclassified as a
generic process issue.

### 4.6 — Investigation Persistence

Investigation routing decisions can be persisted and reloaded.

Runtime acceptance persisted report 807 as an Investigation with its candidate
and selected Specialist state.

### 4.7 — Knowledge Sources

Eight initial official documentation sources were seeded and all nine current
Specialists received source coverage.

### 4.8 — Knowledge RAG

Implemented:

```text
source loading
parsing
structure-aware chunking
KnowledgeDocument / KnowledgeChunk persistence
embedding generation
GIN full-text index
HNSW vector index
hybrid retrieval
RRF fusion
scope reranking
source attribution
```

NGINX acceptance:

```text
document status       indexed
chunks                3
embedded chunks       3
missing embeddings    0
search indexes        2/2
```

Hybrid search returned all three chunks for the NGINX scope and demonstrated
both hybrid and vector-only results.

### 4.9 — Specialist Context Builder

The Context Builder combines:

```text
task
Specialist instructions
current evidence
initial analysis
Incident RAG
Knowledge RAG
```

under explicit budgets.

NGINX acceptance:

```text
knowledge chunks 3
source refs      3
context chars    4923
```

### 4.10 — Specialist Reasoning Agent

The first Specialist LLM integration is reasoning-only.

The no-live-evidence NGINX acceptance correctly returned:

```text
status           completed
confidence       0.10
findings         0
hypotheses       1
missing evidence 5
```

This verified conservative reasoning and the distinction between technical
documentation and operational evidence.

### 4.11 — Diagnostic Tool Registry

The current registry contains:

```text
18 tools
risk = read_only
```

The automated suite after 4.11 is:

```text
124 passed
```

The NGINX Specialist currently has no assigned Tool IDs:

```text
Allowed IDs: —
Tools: 0
```

That is expected. Tool assignment and policy must be explicit before any
execution.

## Search architecture snapshot

### Incident RAG

```text
historical analyses
 -> vector + full-text retrieval
 -> compatibility/semantic gates
 -> RRF
 -> analysis context
```

### Knowledge RAG

```text
technical sources
 -> parse
 -> structure-aware chunks
 -> FTS/GIN + embeddings/HNSW
 -> Specialist/domain scope
 -> RRF
 -> deterministic reranking
 -> bounded technical context
```

The two systems remain separate because historical incident evidence and
technical documentation have different semantics and trust.

## Safety boundary snapshot

Current:

```text
LLM reasoning                  yes
Knowledge retrieval            yes
Incident retrieval             yes
Registered read-only Tools     yes
Tool execution by Specialist   no
Arbitrary shell                no
Remediation                    no
```

Next:

```text
4.12 Diagnostic Policy Engine
4.13 Evidence Collection
4.14 Specialist Investigation Loop
```
