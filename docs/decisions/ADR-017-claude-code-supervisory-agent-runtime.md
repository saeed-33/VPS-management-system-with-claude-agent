# ADR-017 - Claude Code as Supervisory Agent Runtime

Status: **Accepted**

Date: **2026-08-11**

## Context

The project has completed Phase 4.20 and is currently
`ready_for_supervised_operations`. The application already implements the
operational capabilities required for monitoring and autonomous diagnosis,
including monitoring profiles, scheduled monitoring, SSH execution, reports,
analysis, Incident RAG, Knowledge RAG, dynamic Specialists, investigation
persistence, registered read-only diagnostic tools, policy enforcement,
evidence tracking, multi-Specialist correlation, final diagnosis, and
production-readiness evaluation.

The project previously used project-owned Python orchestration, including
LangGraph-based investigation orchestration, to coordinate these capabilities.

A new architectural direction has been accepted: Claude Code becomes the
**primary supervisory orchestration runtime**. Existing project functions remain
the authoritative implementation of monitoring, analysis, retrieval,
investigation, persistence, policy, safety, and infrastructure operations.

This decision does **not** replace existing services with Claude Code and does
**not** reduce the application to a passive UI. The application remains the
control plane, source of truth, safety boundary, persistence layer, and provider
of operational capabilities.

## Decision

Adopt this responsibility split:

```text
Claude Code
  = primary supervisory reasoning and orchestration

Existing Python application
  = operational capabilities, control plane, persistence, policy, safety, UI

Ollama
  = operational LLM provider for project analysis and specialist reasoning

MCP / controlled project tools
  = contract boundary between Claude Code and application capabilities
```

The target execution model is:

```text
Scheduler / operator trigger
      -> Claude Code Supervisor
      -> controlled project tools
      -> existing application services
      -> DB / pgvector / SSH / reports / investigations
      -> Ollama where project LLM reasoning is required
```

Claude Code may decide which existing function to invoke, in which order, and
whether additional investigation is required. It must not reimplement the
internal business logic of those functions.

Examples:

```text
run_monitoring(server_id, profile_id)
get_report(report_id)
analyze_report(report_id)
search_similar_incidents(report_id)
search_knowledge(query, scope)
start_investigation(report_id)
get_available_specialists(context)
run_specialist(specialist_id, investigation_id)
get_investigation_status(investigation_id)
complete_investigation(investigation_id)
test_remediation_in_sandbox(plan_id)
apply_or_request_approval(plan_id)
```

The exact tool surface will be introduced incrementally and validated before
becoming authoritative.

## Fixed operational workflow

The Claude Code transition must preserve this workflow order:

```text
periodic monitoring
 -> per-server subordinate agent
 -> monitoring completion
 -> exact/similar historical report lookup
 -> exact match: reuse previous analysis
 -> similar match: pass top 3 similar reports to the LLM
 -> initial LLM analysis and potential issue discovery
 -> if issues exist: select and run specialist agents
 -> specialist deep analysis
 -> subordinate agent aggregates results
 -> final diagnosis
 -> if a problem exists: propose remediation
 -> test remediation in an isolated environment
 -> apply automatically only when policy allows, otherwise ask the user
```

This workflow is fixed. Claude Code may coordinate decisions inside it, but it
must not skip retrieval, specialist analysis, evidence grounding, policy checks,
persistence, or isolated remediation validation.

## LLM provider decision

Ollama is the operational LLM provider for project analysis, assisted RAG
analysis, specialist reasoning, and final synthesis. Claude Code is the
supervisory orchestration runtime, not a replacement for the project LLM
clients.

The expected boundary is:

```text
Claude Code Supervisor
      -> controlled project tool
      -> existing Python service
      -> configured Ollama client/model
```

Claude Code must not bypass the project LLM clients for report analysis,
specialist reasoning, or persisted diagnosis generation.

## Existing functionality remains authoritative

The following remain project-owned functions and are not moved into Claude
prompts or replaced with unrestricted Claude execution:

```text
Monitoring Profiles
scheduled monitoring
SSH execution
command registry
report generation and persistence
analysis services
Incident RAG
Knowledge RAG
embeddings / pgvector / FTS / retrieval
Specialist definitions and registry
Investigation domain and persistence
Evidence
Policy Engine
registered diagnostic tools
budgets and limits
API / Admin UI
PostgreSQL source of truth
future remediation approvals and audit
```

Claude Code invokes these capabilities through controlled interfaces.

## Claude Code repository structure

The project will adopt a Claude Code-oriented structure, adapted to the project
rather than copied mechanically:

```text
CLAUDE.md
.mcp.json
.claude/
  settings.json
  settings.local.json
  rules/
    monitoring.md
    investigation.md
    specialists.md
    rag.md
    remediation.md
    safety.md
  commands/
    monitor.md
    analyze.md
    investigate.md
    diagnose.md
  skills/
    server-monitoring/
      SKILL.md
    incident-analysis/
      SKILL.md
    specialist-investigation/
      SKILL.md
    remediation-planning/
      SKILL.md
  agents/
    monitoring-supervisor.md
    investigation-coordinator.md
    generic-specialist.md
  hooks/
    ... only where a concrete policy/validation need exists
```

This structure is the agent-control layer. It does not replace `app/`, `tests/`,
`docs/`, or the application services.

## Dynamic Specialists remain dynamic

ADR-008 remains in force.

Specialists are still user-managed definitions persisted by the application. We
will not reintroduce hard-coded CPU, Memory, PostgreSQL, or similar agents as
the source of truth under `.claude/agents/`.

Instead:

```text
generic-specialist
      +
SpecialistDefinition from DB
      +
current task/context
      +
allowed project tools
      -> Specialist execution
```

Static Claude agent files may define generic roles only.

## Scheduler boundary

The existing scheduling capability remains project-owned.

Claude Code is invoked for a bounded monitoring or investigation job. It is not
the long-running timer loop and is not responsible for implementing periodic
scheduling itself.

```text
Project Scheduler
      -> start bounded Claude job
      -> Claude coordinates existing functions
      -> persist result
```

## Safety boundary

Claude Code is not the authorization authority.

The following invariants remain mandatory:

```text
NO unrestricted shell as the normal tool boundary
NO direct arbitrary SSH from Claude
NO bypass of Tool Registry
NO bypass of Policy Engine
NO write-capable production remediation without approval/policy authorization
NO replacement of persisted Specialist permissions with prompt-only permissions
NO bypass of sandbox remediation validation
```

A Claude request for an operation is a **request**, not an authorization
decision.

Remediation remains gated even after Claude Code becomes the main supervisor.
The fixed workflow allows remediation proposal and isolated-environment testing,
but real production application must be authorized by the project policy and
must ask the user whenever risk or approval rules require it.

## LangGraph consequence

ADR-010 and ADR-014 describe the currently accepted LangGraph orchestration
boundary and implementation. They remain historically valid for the implemented
Phase 4 system, but this ADR changes the forward architectural direction.

LangGraph is **not removed immediately**.

During transition:

```text
existing Python/LangGraph orchestration
              +
new Claude supervisory path
```

Both may coexist until equivalence and safety acceptance tests pass. Only after
the Claude supervisory path demonstrates equivalent or better behavior may
duplicated orchestration be deprecated.

Existing domain logic, services, retrieval, policy, evidence, and persistence
are not candidates for removal merely because Claude Code is introduced.

## Migration principle

The migration must be additive first and subtractive only after acceptance:

```text
Add Claude boundary
 -> expose one existing capability
 -> run controlled end-to-end acceptance
 -> expand capability surface
 -> compare with current execution
 -> switch orchestration ownership
 -> only then remove duplicated orchestration
```

No big-bang rewrite is authorized by this ADR.

## Consequences

Positive:

```text
preserves implemented and tested project functionality
reduces future custom agent-orchestration complexity
makes Claude Code the high-level reasoning coordinator
retains deterministic safety boundaries
keeps the Admin UI and database authoritative
keeps Specialists dynamic and user-managed
allows progressive migration with rollback
provides a clear place for Claude rules, skills, agents, commands, and MCP
```

Costs and risks:

```text
introduces an additional runtime dependency and process boundary
requires strict MCP/tool contracts and runtime failure handling
requires cost, timeout, turn, concurrency, and session observability
creates a temporary period with two orchestration paths
requires new acceptance tests before old orchestration can be retired
```

## Acceptance criteria for this architectural transition

The architectural transition is not complete until the Claude supervisory path
can demonstrate all of the following using existing project capabilities:

```text
scheduled monitoring trigger works
monitoring results remain equivalent/persisted
fixed operational workflow order is preserved
analysis and RAG remain project-owned and callable
Ollama provider availability and structured-output behavior are validated
investigation can be started and persisted
Specialist definitions remain DB-driven
multiple Specialists can be coordinated safely
evidence provenance remains valid
policy/budget enforcement cannot be bypassed
runtime failure is recoverable and auditable
remediation proposals are sandbox-tested before production application
production application asks the user whenever policy requires approval
current Phase 4 safety metrics do not regress
```

## Related decisions

- ADR-008 - Dynamic user-defined specialists
- ADR-009 - Hierarchical bounded read-only investigation
- ADR-010 - LangGraph orchestration boundary
- ADR-011 - Dual RAG and Knowledge Retrieval
- ADR-012 - Specialist reasoning and provenance boundary
- ADR-013 - Registered read-only diagnostic tools
- ADR-014 - LangGraph Investigation Orchestration
- ADR-015 - Dynamic Secondary Specialist Routing
- ADR-016 - Production Readiness and Remediation Boundary

## Implementation plan

See:

`docs/roadmap/claude-code-supervisory-transition-plan.md`
