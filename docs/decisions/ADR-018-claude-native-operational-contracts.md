# ADR-018 - Claude-Native Operational Contracts

Status: **Accepted**

Date: **2026-08-12**

## Context

ADR-017 established Claude Code as the intended supervisory orchestration
runtime while keeping Python services authoritative for execution, persistence,
policy, evidence, RAG, SSH, and the Admin/API control plane.

The first transition implementation created the expected Claude Code repository
surface (`.claude/`, `.mcp.json`, agents, skills, rules, commands, and settings),
but later review found an architectural mismatch:

```text
intended
Claude owns high-level workflow decisions
Python owns safe deterministic capabilities

current transition state
Python still sequences monitoring and Specialist workflows
Claude-facing files describe the intended workflow but do not yet own it
```

The repository also accumulated duplicated prompt layers: commands repeated
skills, workflow rules repeated skills and agents, and the hooks directory
contained a placeholder rather than an enforced runtime hook.

A previous prototype, `Safe-AI-VPS-Agent-claude`, demonstrated a more useful
Claude-native pattern: operational skills define executable workflows and
bounded agents define precise worker contracts. The current project must adopt
that pattern without copying the prototype's unsafe direct-shell/credential
handling.

## Decision

Clarify ADR-017 with the following responsibility split:

```text
Claude Code
  = reasoning, sequencing, branching, task decomposition, synthesis

.claude/skills
  = operational workflow contracts

.claude/agents
  = bounded intelligent worker contracts

MCP
  = the only project-capability interface exposed to Claude

Python
  = deterministic execution, validation, policy, persistence, safety

PostgreSQL
  = source of truth

Ollama
  = LLM provider for the Claude runtime and project-owned LLM reasoning
```

The governing rule is:

```text
Claude decides WHAT to do next.
Python decides WHETHER the request is allowed and HOW it is executed safely.
```

### Operational skills, not workflow notes

A production skill must define, as applicable:

```text
purpose
inputs
allowed tools
preconditions
workflow
branch conditions
validation after tool calls
failure and retry behavior
stopping conditions
output contract
```

A short prose note that merely repeats the architecture is not accepted as an
operational skill.

### Bounded agents, not role descriptions

A production agent contract must define, as applicable:

```text
inputs
responsibility
allowed tools
hard boundaries
skills
budgets
failure behavior
output contract
```

Static Claude agents do not become the source of truth for domain Specialists.
Dynamic `SpecialistDefinition` records remain authoritative.

### MCP-only operational capability path

Claude must not receive a normal-operation capability for:

```text
raw SSH
arbitrary shell
raw SQL
direct database access
direct production remediation
```

Operational calls use project MCP tools, which invoke project services and
retain all existing policy, evidence, persistence, budget, and SSH boundaries.

### Rules contain invariants only

Global `.claude/rules/` files are reserved for cross-workflow invariants.
Workflow procedures belong in skills.

The baseline global rules are:

```text
safety.md
evidence-grounding.md
```

Additional rules require a distinct cross-workflow invariant that cannot be
expressed more appropriately in an operational skill or agent contract.

### Commands are removed

`.claude/commands/` is removed from the project-owned runtime specification.
User/operator workflows are represented as skills instead of maintaining a
second prompt surface that duplicates the same procedure.

### Hooks exist only when they enforce something

A hooks directory or hook file is not created to document a future idea.
Hooks may be introduced only with a concrete enforcement or audit requirement,
such as runtime preflight, guarded tool use, subagent lifecycle audit, or safe
session completion.

### Current transition truth

Until C.14's runtime acceptance tests pass, the project must not claim that
production scheduling is truly Claude-native.

The current scheduler-facing path still uses Python orchestration wrappers.
Those wrappers remain temporarily for compatibility and are removed or demoted
only after a real Claude session path proves equivalent and safe.

## C.14 execution sequence

```text
C.14.0  Architecture decision
C.14.1  Remove cosmetic/duplicated Claude surfaces
C.14.2  Operational Skills
C.14.3  Bounded Agents
C.14.4  Least privilege and model inheritance
C.14.5  Concrete Hooks
C.14.6  ClaudeSessionRunner
C.14.7  Ollama-backed Claude runtime
C.14.8  MCP boundary refactor
C.14.9  Remove duplicate Python orchestration
C.14.10 Session/job observability
C.14.11 Runtime acceptance tests
C.14.12 Readiness and safety reevaluation
C.14.13 Documentation synchronization
C.14.14 Phase C closure
```

Phase 5 is blocked until C.14.14.

## Safety consequences

This ADR does not expand production permissions.

```text
automatic_remediation_allowed = false
```

The existing Python Policy, Evidence, Specialist permissions, budgets, SSH
implementation, persistence, and remediation gates remain authoritative.

## Relationship to previous decisions

ADR-017 remains accepted and defines the high-level Claude supervisory
direction. ADR-018 clarifies what "Claude supervisory runtime" means
operationally and corrects the structure-only interpretation.

ADR-008, ADR-009, ADR-011, ADR-012, ADR-013, ADR-015, and ADR-016 remain in
force.

## Acceptance

C.14 cannot close until all of the following are demonstrated:

```text
scheduler starts a real bounded Claude session
Claude runtime is launched through the configured Ollama path
project MCP tools are visible to that session
operational skills participate in real workflow execution
agents participate in real workflow execution
Specialists remain DB-defined
high-level workflow sequencing is not duplicated in Python
no raw SSH, SQL, or unrestricted shell path is exposed
evidence grounding and budgets remain enforced
provider/runtime failures are controlled and auditable
runtime readiness and safety gates pass on the new path
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
