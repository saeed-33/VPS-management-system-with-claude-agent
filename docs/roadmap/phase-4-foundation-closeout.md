# Phase 4 Milestone A Closeout — Foundation

**Scope:** 4.0–4.4  
**Status:** Completed

Delivered:

```text
4.0 Architecture / roadmap / ADR baseline
4.1 Investigation contracts
4.2 Dynamic Specialist model + database
4.3 Specialist management API + UI
4.4 Specialist Registry runtime service
```

Acceptance at closeout:

```text
57 automated tests passed
9 enabled Specialist definitions loaded
cpu -> linux-cpu
cpu + process -> deterministic multi-domain candidates
```

Current boundary:

```text
Operator
 -> Specialist Management UI/API
 -> SpecialistDefinitionService
 -> SpecialistDefinitionRepository
 -> PostgreSQL
 -> SpecialistRegistry
 -> SpecialistRegistrySnapshot
 -> Phase 4.5 Investigation Router
```

Not yet implemented: real report routing to Specialists, Specialist LLM reasoning, diagnostic tool execution, investigation persistence, LangGraph runtime orchestration, or remediation.

Next milestone starts with **4.5 — Investigation Router**.
