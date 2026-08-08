# ADR-010 — LangGraph Orchestration Boundary

**Status:** Accepted  
**Phase:** 4

LangGraph will be used only for stateful investigation orchestration when Phase 4 reaches iterative and multi-agent workflows.

It will not replace the project's domain services, repositories, persistence, RAG, SSH implementation, policy engine, Specialist Registry, or Tool Registry.

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
SSH Executor
      |
-------------------------------
          LangGraph
 Investigation orchestration
-------------------------------
      |
LLM reasoning
```

User-defined specialists must not become hard-coded graph nodes such as `cpu_agent` or `memory_agent`. The graph will use generic nodes that receive a dynamic Specialist definition/task.

LangGraph does not authorize or directly execute arbitrary shell commands. Future execution remains:

```text
LLM structured request
 -> Tool Registry
 -> Policy Engine
 -> parameter validation
 -> known read-only implementation
 -> SSH Executor
```

LangGraph is deliberately not introduced in Foundation steps 4.0–4.4. It enters later when iterative loops, conditional branches, parallel specialists, and coordinator workflows are required.
