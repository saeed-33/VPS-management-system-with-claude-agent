# Testing and Evaluation

Run the automated suite:

```powershell
uv run python -m pytest
```

## Current automated baseline

After Phase 4.11 acceptance:

```text
124 passed
```

One Starlette/httpx deprecation warning remains and is not a functional test
failure.

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
Reasoning citation validation
Specialist recommendation normalization
Diagnostic Tool Registry
Tool parameter safety
Specialist Tool allow-list enforcement
```

## Runtime acceptance checkpoints

### Router

Healthy report:

```text
report 825
should investigate false
selected specialists 0
```

Connection failure:

```text
report 807
domains connectivity, network
selected linux-network
```

### Knowledge Sources

```text
enabled sources       8
covered specialists   9/9
acceptance             PASS
```

### Knowledge ingestion/chunking/indexing

NGINX source:

```text
document ID           1
characters            3731
chunks                3
status                indexed
embedded chunks       3
missing embeddings    0
embedding dimensions  768
search indexes        2/2
acceptance             PASS
```

### Knowledge Hybrid Retrieval

Query:

```text
nginx modules configuration
specialist nginx
domains nginx,http,proxy
```

Result:

```text
3 chunks
rank 1 strategy hybrid
ranks 2-3 strategy vector
source nginx-docs
```

This validates retrieval mechanics.

It does **not** prove corpus quality. The current source is the NGINX index
page, so some retrieved content is navigation/module-list material.

### Specialist Context Builder

NGINX preview:

```text
knowledge chunks 3
source refs      3
context chars    4923
```

The rendered context preserved Specialist instructions and Knowledge chunk
provenance.

### Specialist Reasoning

No operational NGINX evidence was supplied.

Expected conservative behavior was observed:

```text
status           completed
confidence       0.10
findings         0
hypotheses       1
missing evidence 5
```

The model requested service/log/listener/upstream evidence instead of claiming
those facts were known.

### Diagnostic Tool Registry

```text
tools   18
risk    read_only
```

Injection/path/port/unknown-argument tests validate command rendering safety.

The current NGINX Specialist has:

```text
Allowed IDs: —
Tools: 0
```

This is correct until explicit Tool permissions are assigned.

## Controlled real-server evaluation environment

Reference target:

```text
Ubuntu Server 22.04.2 amd64
VMware
```

A workload simulator is used to create repeatable ground-truth scenarios such
as:

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

This environment should be used for integration/evaluation beginning with Tool
execution and the Specialist investigation loop.

## Evaluation principle

Automated unit tests answer:

```text
"Does the implementation obey its contracts?"
```

Controlled VM scenarios answer:

```text
"Does the investigation reach the correct diagnosis from real evidence?"
```

Both are required before Phase 4 closes.

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
