# ADR-010 — LangGraph Orchestration Boundary

**Status:** Accepted and implemented  
**Phase:** 4.16–4.17

LangGraph is used only for stateful investigation orchestration. It does not replace the project's domain services, repositories, persistence, RAG, SSH implementation, policy engine, Specialist Registry, Tool Registry, or Evidence contracts.

```text
FastAPI / UI
      |
Application Services
      |
Repositories / PostgreSQL / pgvector
      |
Specialist Registry
Knowledge RAG
Incident RAG
Tool Registry
Policy Engine
Evidence Collection
SSH Executor
      |
-------------------------------
          LangGraph
 Investigation orchestration
-------------------------------
      |
LLM reasoning
```

## Implemented boundary

Phase 4.16 introduced a generic LangGraph parallel Coordinator for dynamic Specialists.

Specialists do not become hard-coded graph nodes such as `cpu_agent` or `memory_agent`. Runtime Registry definitions are passed through generic worker state.

Phase 4.17 composes an outer bounded follow-up workflow above the accepted 4.16 parallel wave:

```text
initial routing
 -> parallel specialist wave
 -> collect recommendations
 -> validate Registry/budgets/duplicates
 -> optional next parallel wave
 -> repeat while bounded
```

Specialists inside one wave may execute concurrently. Follow-up waves are sequential because later routing depends on results and Evidence from earlier waves.

## Safety boundary

LangGraph does not authorize or directly execute arbitrary shell commands.

Execution remains:

```text
LLM structured request
 -> Tool Registry
 -> Policy Engine
 -> parameter validation
 -> approved execution envelope
 -> Evidence Collection
 -> known read-only SSH implementation
```

## State and budget ownership

Parallel workers do not mutate one shared Python action counter.

The Coordinator pre-allocates deterministic worker quotas such that:

```text
sum(worker.action_quota) <= InvestigationBudget.max_actions
```

Phase 4.17 then deducts actual wave usage from the global remaining budget before any secondary wave.

The model cannot create an executable Specialist. A recommended slug must exist in the enabled Registry and pass duplicate and budget checks.

## Consequence

LangGraph remains an orchestration runtime, not the source of truth for Specialists, security policy, RAG, persistence, SSH, or Evidence.

This boundary allows new operator-defined Specialists to be added without modifying the graph structure.
