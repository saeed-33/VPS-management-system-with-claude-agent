# LangGraph Investigation Orchestration

**Phase:** 4.16  
**Decision:** LangGraph is the orchestration runtime for the multi-Specialist
Investigation workflow.

## Why LangGraph

The project already owns its domain logic:

- Investigation Router
- dynamic Specialist Registry
- Specialist reasoning loop
- RAG
- Diagnostic Tool Registry
- Policy Engine
- SSH execution
- Evidence contracts

LangGraph is used only for stateful orchestration. It does not replace those
services and does not require LangChain agents.

The graph introduced in 4.16 is:

```text
START
  |
  v
prepare
  |
  +---- no selected workers ----> aggregate ----> END
  |
  `---- Send(worker A) --+
       Send(worker B) ---+--> aggregate --> END
       Send(worker N) ---+
```

`Send` provides dynamic fan-out because Specialist count and identity are
runtime Registry data.

## State ownership

Parallel workers share immutable baseline input:

- Investigation identity
- report/server/analysis identifiers
- routing decision
- baseline Evidence
- allowed Specialist slugs

Workers do not mutate a shared Python action counter.

Each worker emits one `ServerCoordinatorSpecialistRun` into a reducer-backed
list. Aggregation sorts those runs using routing selection order, making final
ordering deterministic even when completion order is not.

## Global action budget under parallelism

A sequential mutable counter cannot safely control independent parallel
branches.

Phase 4.16 therefore uses deterministic pre-allocation:

```text
Investigation max_actions = 5
Selected workers = 2

worker 1 quota = 3
worker 2 quota = 2

sum quotas = 5
```

The allocation invariant is:

```text
sum(worker.action_quota) <= InvestigationBudget.max_actions
```

Each worker receives its own `InvestigationBudget(max_actions=quota)` and
starts its local action counter at zero.

This is intentionally conservative. Unused quota from one worker is not
borrowed by another during the same fan-out superstep. Dynamic redistribution
can be considered later only if it can preserve deterministic budget safety.

## Failure isolation

A worker catches its own Specialist-loop exception and converts it to a failed
`SpecialistResult`.

Therefore one failed branch does not abort successful sibling branches.

This is important because an uncaught exception in a parallel LangGraph
superstep can fail that superstep.

## What remains unchanged

LangGraph does not execute shell commands, authorize Tools, retrieve RAG
documents, or invoke SSH directly.

The execution boundary remains:

```text
LangGraph worker
 -> SpecialistInvestigationLoop
 -> Diagnostic Policy
 -> Evidence Collection
 -> existing SSH stack
```

## Persistence boundary

4.16 compiles the graph without a production checkpointer.

This is deliberate: the first acceptance target is orchestration equivalence
plus safe parallelism.

A Postgres LangGraph checkpointer should be introduced as a separate persistence
step after graph state has stabilized. The project already uses PostgreSQL, so
that later step does not require adopting a second database technology.

## Roadmap alignment

- 4.15: sequential Server Coordinator — complete
- 4.16: LangGraph foundation + bounded parallel fan-out — this phase
- 4.17: conditional secondary Specialist routing
- 4.18: cross-Specialist correlation and final diagnosis

The existing `ServerCoordinator` is retained as the sequential reference
implementation and compatibility boundary while 4.16 is accepted.
