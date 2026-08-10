# ADR-014: LangGraph for Investigation Orchestration

**Status:** Accepted  
**Phase:** 4.16

## Context

The Investigation workflow is no longer a simple linear service call. It now
contains dynamic routing, independent Specialists, per-Specialist reasoning
loops, Evidence collection, global budgets, and future secondary routing and
cross-Specialist synthesis.

Continuing with hand-written orchestration would require the project to own
parallel fan-out/fan-in, graph state transitions, checkpoint semantics, resume
behavior, and later human-in-the-loop control.

## Decision

Use LangGraph as the low-level orchestration runtime for Phase 4
multi-Specialist Investigations.

LangGraph is an orchestration dependency only.

The project retains its existing:

- Ollama/OpenAI clients
- Specialist Registry
- RAG services
- Diagnostic Tool Registry
- Diagnostic Policy Engine
- SSH execution
- Evidence and Investigation domain contracts

LangChain agents are not required.

## Consequences

### Positive

- Dynamic Specialist fan-out maps directly to LangGraph `Send`.
- Parallel result accumulation uses explicit reducers.
- Later checkpoint/resume and human approval can use LangGraph primitives.
- Nodes remain ordinary Python functions calling project services.
- Agent topology becomes inspectable rather than hidden in nested loops.

### Constraints

- LangGraph state must remain domain-focused and should not become a dumping
  ground for service objects.
- Global mutable budgets must not be concurrently modified by worker nodes.
- Parallel output order must never be assumed to equal completion order.
- Policy/SSH safety boundaries remain outside LangGraph.
- Persistence is not enabled in 4.16; Postgres checkpointing is a separate
  acceptance step.

## Alternatives

### Hand-written asyncio orchestration

Rejected as the long-term architecture. It is viable for simple concurrency,
but the project would then need to implement graph state, routing transitions,
resume/checkpoint semantics, and future human-in-the-loop behavior itself.

### Replace existing services with LangChain agents

Rejected. The existing contracts and safety boundaries are already explicit,
tested, and application-specific. Replacing them would add abstraction without
solving the orchestration problem.

## Follow-up

4.17 adds conditional secondary Specialist routing to the graph.

4.18 adds correlation and final diagnosis nodes.
