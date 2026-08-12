# C.14 - Claude-Native Execution Plan

## Goal

Convert the current Claude transition from a configuration/scaffolding layer
into the actual bounded supervisory runtime before Phase 5 begins.

## Non-goals

C.14 does not introduce production write remediation, autonomous repair,
unrestricted shell, raw SSH, raw SQL, or hard-coded domain Specialists.

## Target architecture

```text
Scheduler
   |
ClaudeSupervisor
   |
Claude session launched through Ollama
   |
server supervisor + operational skills
   |
project MCP
   |
Project Tool Registry
   |
Python domain services / policy / evidence
   |
DB / SSH / RAG / Ollama
```

## Work breakdown

### C.14.0 - Architecture decision

Status: **COMPLETE after this change set**

Deliverables:

- ADR-018
- explicit runtime ownership rule
- Phase 5 remains blocked until C.14 closes

### C.14.1 - Remove cosmetic/duplicated Claude surfaces

Status: **COMPLETE after this change set**

Deliverables:

- remove `.claude/commands/`
- remove workflow-specific global rules
- keep global rules limited to safety and evidence grounding
- remove placeholder hooks documentation
- add tests preventing reintroduction of cosmetic surfaces
- mark existing skills/agents as transitional pending C.14.2/C.14.3

### C.14.2 - Operational Skills

Status: **COMPLETE**

Replace the current short workflow notes with operational contracts:

```text
monitor-server
analyze-incident
investigate-incident
plan-remediation
```

Each skill must define inputs, allowed tools, preconditions, branching,
validation, failure behavior, stopping conditions, and output contract.

No production remediation is authorized.

### C.14.3 - Bounded Agents

Status: **NEXT**

Target static agent roles:

```text
server-supervisor
specialist-worker
```

The server supervisor is the main per-server session agent. The specialist
worker executes one DB-defined Specialist task. Static files never become the
source of truth for CPU/Memory/PostgreSQL/etc. Specialists.

### C.14.4 - Least privilege and model inheritance

Status: **PENDING**

- replace hard-coded `model: sonnet` with `model: inherit`
- restrict each agent to only required MCP tools
- remove nested-agent assumptions that are not supported by the runtime design
- keep production remediation unavailable

### C.14.5 - Concrete Hooks

Status: **PENDING**

Only introduce hooks with real enforcement/audit value.

Candidate responsibilities:

```text
SessionStart -> runtime preflight
PreToolUse -> defense-in-depth guard/audit
Subagent lifecycle -> job correlation/audit
Stop -> prevent silent incomplete session termination
```

### C.14.6 - ClaudeSessionRunner

Status: **PENDING**

Implement the concrete process/session runner used by `ClaudeSupervisor`.
The scheduler must stop calling a Python workflow sequencer as its Claude
runtime implementation.

### C.14.7 - Ollama-backed Claude runtime

Status: **PENDING**

Add explicit runtime configuration and launch the real session through the
supported Ollama-to-Claude Code integration. The selected agent model must
inherit from the session.

### C.14.8 - MCP boundary refactor

Status: **PENDING**

Refactor the large project boundary into domain tool handlers/registries while
keeping MCP as a thin schema/dispatch compatibility layer.

### C.14.9 - Remove duplicate Python orchestration

Status: **PENDING**

After parity tests pass, remove or demote Python components that encode
Claude-owned high-level sequencing, including the deterministic monitoring and
multi-Specialist supervisor loops.

Python keeps deterministic validation, execution, policy, persistence, budgets,
timeouts, and safety.

### C.14.10 - Session/job observability

Status: **PENDING**

Persist enough runtime data to answer:

```text
which session ran
which server/cycle it belonged to
which agent and skills were involved
which tools were called
how many turns/tool calls were consumed
why the session stopped
what failure occurred
```

### C.14.11 - Runtime acceptance tests

Status: **PENDING**

Required coverage includes:

```text
real MCP subprocess initialize/list/call
Claude-through-Ollama smoke path
monitoring cycle
exact/similar/no-history analysis branches
DB-defined Specialist selection
budget enforcement
forbidden SSH/SQL/shell attempts
provider/MCP/DB failure behavior
concurrent per-server session isolation
```

### C.14.12 - Readiness and safety reevaluation

Status: **PENDING**

Re-run the accepted Phase 4/Phase C safety metrics against the new execution
path. Previous evidence does not automatically prove the new runtime safe.

### C.14.13 - Documentation synchronization

Status: **PENDING**

Synchronize project status, architecture, operations, workflow, test catalog,
and generated structure documentation with the accepted runtime.

### C.14.14 - Phase C closure

Status: **PENDING**

Phase C closes only after all C.14 acceptance gates pass.

Then, and only then, Phase 5 - Supervised Remediation begins.
