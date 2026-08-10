# LangGraph Investigation Orchestration

**Phase:** 4.16–4.17  
**Status:** Implemented and runtime accepted.

LangGraph is the orchestration runtime for multi-Specialist Investigation. The project continues to own all domain and safety logic.

LangGraph does not replace:

- Investigation Router
- dynamic Specialist Registry
- Specialist reasoning loop
- Incident RAG
- Knowledge RAG
- Diagnostic Tool Registry
- Diagnostic Policy Engine
- Evidence Collection
- SSH execution
- Investigation contracts

No LangChain agent abstraction is required.

## Phase 4.16 inner graph

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

`Send` performs dynamic fan-out because Specialist identities come from runtime Registry data.

## Parallel state ownership

Workers share immutable baseline input and emit reducer-backed Specialist runs.

They do not mutate one shared Python action counter.

Aggregation restores deterministic output ordering from routing selection order even if workers finish in a different order.

## Parallel action budget

The global action budget is pre-allocated conservatively across workers.

```text
max_actions = 8
workers = 2

worker A quota = 4
worker B quota = 4
```

Invariant:

```text
sum(worker.action_quota) <= InvestigationBudget.max_actions
```

Unused quota is not borrowed by a sibling during the same parallel superstep.

## Failure isolation

A worker failure is converted into a failed Specialist result. It does not automatically abort successful sibling workers.

## Phase 4.17 outer graph

Phase 4.17 adds sequential dynamic waves around the accepted parallel graph:

```text
wave 1
 -> inspect recommendations
 -> validate Registry/budgets/duplicates
 -> optional wave 2
 -> ...
 -> finalize
```

This creates two orchestration levels:

```text
outer graph = conditional secondary routing
inner graph = bounded parallel Specialist execution
```

## Execution boundary

LangGraph never executes shell commands directly.

```text
LangGraph worker
 -> SpecialistInvestigationLoop
 -> Diagnostic Policy
 -> Evidence Collection
 -> existing SSH stack
```

## Runtime acceptance

Phase 4.16 controlled parallel acceptance proved two real Specialist loops can run through the LangGraph runtime while preserving quota and global-budget invariants.

Phase 4.17 controlled secondary acceptance then proved two sequential waves with real Registry/budget validation and real secondary Specialist execution.

## Persistence boundary

The graph remains compiled without a production LangGraph checkpointer.

Investigation persistence remains a project-owned concern. A Postgres LangGraph checkpointer may be added later only if required by resumability semantics; it is not required for the accepted 4.16/4.17 orchestration behavior.

## Roadmap

- 4.15 sequential Server Coordinator: complete
- 4.16 LangGraph parallel orchestration: complete
- 4.17 dynamic secondary routing: complete
- 4.18 cross-Specialist correlation and final diagnosis: next
