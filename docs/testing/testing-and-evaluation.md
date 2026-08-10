# Testing and Evaluation

Run the automated suite:

```powershell
uv run python -m pytest
```

## Current automated baseline

After accepted Phase 4.17 work:

```text
184 passed, 1 warning
```

The remaining warning is the existing Starlette/TestClient deprecation warning and is not a Phase 4.17 functional failure.

## Covered Phase 4 areas

The suite now includes coverage for:

```text
Investigation contracts
Dynamic Specialist persistence/API/registry
FastAPI route inventory
Investigation routing
Investigation persistence
Knowledge Sources
Knowledge ingestion/parsing
Structure-aware chunking
Knowledge indexing
Knowledge hybrid retrieval/scope
Specialist Context Builder
Specialist Reasoning Agent
Reasoning citation/provenance validation
Specialist recommendation normalization
Diagnostic Tool Registry
Tool parameter safety
Specialist Tool allow-list enforcement
Diagnostic Policy Engine
Evidence Collection
Specialist Investigation Loop
Server Coordinator
LangGraph parallel orchestration
Dynamic secondary Specialist routing
global specialist/action budget invariants
duplicate Specialist suppression
compact Final Synthesis output
```

## Runtime acceptance checkpoints

### Router

Healthy reports must not open investigations simply because Specialists exist.

Failure reports must detect relevant domains and select only enabled matching Specialists.

### Knowledge RAG

Knowledge retrieval validates mechanics, metadata scope, and source attribution separately from corpus quality.

Technical documentation explains technology behavior but does not prove a live server condition.

### Specialist Reasoning

Reasoning must remain conservative when live operational Evidence is absent.

Unknown Evidence/Knowledge IDs fail provenance validation.

### Diagnostic safety

Required negative cases include:

```text
unknown Tool rejected
Tool not assigned rejected
unknown argument rejected
invalid service/path/port rejected
shell injection rejected
Policy DENY never reaches SSH
```

No arbitrary shell is permitted.

### Evidence Collection

Only an approved execution envelope may reach the SSH execution layer.

Command output is bounded and provenance metadata is retained.

### Specialist Investigation Loop

Validate:

```text
bounded rounds
bounded actions
duplicate request suppression
Evidence propagation
objective discipline
final synthesis
no-progress termination
failure handling
```

### LangGraph Parallel — Phase 4.16

Validate:

```text
multiple workers
deterministic worker quotas
sum(worker quotas) <= global max_actions
no state/evidence leakage
deterministic aggregation
partial failure isolation
```

### Dynamic Secondary — Phase 4.17

Controlled acceptance reference:

```text
Status:                  completed
Execution mode:          dynamic-secondary
Waves completed:         2
Actions used:            3/10
Executed Specialists:    nginx, systemd-service
Secondary requested:     systemd-service
Secondary accepted:      systemd-service
```

The controlled acceptance changes only the recommendation value needed to guarantee the secondary path. Primary/secondary Specialist execution and Registry/budget validation remain real.

This proves orchestration correctness, not universal LLM recommendation quality.

## Ollama structured-output reliability

Reference accepted runtime:

```text
CONTEXT = 32768
```

Normal reasoning uses the rich output contract. Final Synthesis uses the compact output contract.

Context capacity and generation capacity are separate settings.

## Controlled real-server evaluation environment

Reference target:

```text
Ubuntu Server 22.04.2 amd64
VMware
```

Ground-truth scenarios include:

```text
baseline
CPU load
memory load
disk I/O
HTTP/network activity
process churn
application errors
failed systemd unit
mixed workload
```

## Evaluation principle

Automated tests answer:

```text
Does the implementation obey its contracts?
```

Controlled VM scenarios answer:

```text
Does the investigation reach the correct diagnosis from real evidence?
```

Both are required before Phase 4 closes.

## Phase 4.18 target

Correlation + Final Diagnosis must test:

```text
common-process correlation
conflicting Specialist conclusions
insufficient Evidence
confirmed/probable/unknown classification
claim-to-Evidence traceability
no unsupported global diagnosis
```

## Phase 4.20 target evaluation dimensions

```text
routing correctness
specialist usefulness
diagnostic accuracy
source attribution
unsupported claims
actions/rounds
LLM calls
latency
token/cost profile
safety violations
```
