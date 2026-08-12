# AI VPS Management - Claude Code Runtime Contract

## Current project phase

The project is in:

```text
Phase C
C.14 - Real Claude-Native Orchestration
```

Phase 4 autonomous diagnosis capabilities are accepted. Production automatic
remediation is not authorized.

The current transition is not complete: project MCP capability exposure exists,
but scheduled production execution still contains Python-owned orchestration
that must be replaced by a real bounded Claude session before Phase C closes.

## Runtime responsibility split

```text
Claude Code
  = reasoning, sequencing, branching, task decomposition, synthesis

.claude/skills
  = operational workflow contracts

.claude/agents
  = bounded intelligent worker contracts

MCP
  = only normal operational capability interface exposed to Claude

Python application
  = deterministic execution, validation, persistence, policy, evidence, safety

PostgreSQL
  = source of truth

Ollama
  = configured LLM provider
```

Core rule:

```text
Claude decides WHAT/NEXT.
Python decides WHETHER ALLOWED and HOW TO EXECUTE SAFELY.
```

## Fixed product workflow

Preserve this product-level order:

```text
periodic monitoring
 -> per-server Claude session
 -> monitoring completion
 -> exact historical report lookup
 -> exact match: reuse stored analysis
 -> otherwise retrieve top similar historical reports
 -> Ollama-backed analysis
 -> issue detection
 -> DB-defined Specialist selection when needed
 -> bounded specialist investigation
 -> evidence-grounded aggregation
 -> final diagnosis
 -> remediation proposal when needed
 -> isolated validation when implemented/available
 -> production action only through Phase 5+ policy/approval contracts
```

The workflow order is fixed at the product level. Claude owns allowed branch and
next-step decisions inside that contract once the real runtime path is enabled.

## Source-of-truth boundaries

Do not reimplement these inside prompts:

```text
monitoring execution
SSH execution
report persistence
Incident RAG
Knowledge RAG
embeddings / pgvector / FTS
dynamic Specialist definitions
DiagnosticToolRegistry
DiagnosticPolicyEngine
Evidence persistence/validation
budgets
remediation authorization
database persistence
Admin/API control plane
```

Use project MCP tools.

## Dynamic Specialists

Specialists are database-managed definitions.

Do not create hard-coded CPU, Memory, PostgreSQL, Nginx, or similar static Claude
agent files as the domain source of truth.

A generic Specialist worker may execute:

```text
SpecialistDefinition from DB
+ current task
+ allowed tool IDs
+ budgets
+ current Evidence
+ retrieved Knowledge
```

## Evidence and reasoning

Historical incidents and technical documentation are context, not proof of the
current server state.

Operational claims about current server state require current report data or
persisted Evidence returned by project services.

Never fabricate:

```text
Evidence IDs
Knowledge IDs
Claim IDs
Conflict IDs
Investigation IDs
Report IDs
Analysis IDs
Remediation IDs
```

## Safety invariants

Claude requests operations. Python authorizes them.

Forbidden normal-operation paths:

```text
unrestricted shell
raw production SSH
raw production SQL
direct database writes
bypass of DiagnosticToolRegistry
bypass of DiagnosticPolicyEngine
bypass of SpecialistDefinition permissions
bypass of budgets
bypass of Evidence validation
production remediation without project authorization
```

Project LLM reasoning must use the configured Ollama path.

## `.claude` design rule

Keep only runtime artifacts with a concrete responsibility.

```text
skills
  operational workflow contracts

agents
  bounded worker contracts

rules
  global invariants only

hooks
  only concrete enforcement/audit hooks
```

Do not recreate `.claude/commands/` as a duplicate workflow surface.

Do not add placeholder hooks or workflow-specific rules that merely repeat
skills.

## Current C.14 implementation boundary

C.14.0 and C.14.1 established the architecture and removed duplicated/cosmetic
Claude surfaces. C.14.2 replaces the workflow-note skills with operational
contracts grounded in the current project MCP tool surface.

C.14.3 establishes two bounded project agent contracts: `server-supervisor`
and `specialist-worker`. `server-supervisor` is intended to run as the main
per-server session agent and may delegate only `specialist-worker` tasks.
`specialist-worker` cannot delegate further.

The agent and Skill contracts are accepted project runtime specifications.
C.14.4 applies least-privilege runtime permissions: both runtime agents use
`permissionMode: dontAsk`, only current MCP capabilities are pre-approved,
raw operational SSH/SQL paths are denied for Bash and PowerShell, and Phase 5
remediation execution tools are explicitly denied.

These contracts are still not proof that a real Claude session is executing
the production workflow. The concrete session runner remains pending.

Before Phase 5, C.14 must still implement and prove:

```text
least-privilege session/settings permissions
concrete hooks where justified
real ClaudeSessionRunner
Ollama-backed Claude launch
Claude-owned workflow sequencing
runtime observability
runtime acceptance tests
readiness/safety reevaluation
```

## Development rule

Before adding a Python high-level workflow branch, ask whether that decision
belongs to Claude. If Claude can make the decision using structured project
tools, expose the capability and keep the decision in Claude.

Do not remove existing deterministic orchestration until the real Claude path
passes equivalence and safety tests.

## Required references

Read before changing the transition:

```text
docs/PROJECT_STATUS.md
docs/decisions/ADR-017-claude-code-supervisory-agent-runtime.md
docs/decisions/ADR-018-claude-native-operational-contracts.md
docs/roadmap/claude-runtime-implementation-plan.md
docs/roadmap/c14-claude-native-execution-plan.md
```

## C.14.5 Runtime Hooks

The project has concrete runtime-only Claude hooks:

- `SessionStart` injects runtime contract context for `server-supervisor`.
- `UserPromptSubmit` blocks a `server-supervisor` prompt when the local
  C.14 runtime contract is not ready (Ollama provider declaration, project
  root, MCP wiring, permission mode, agent contracts, and Phase 5 denials).
- `ConfigChange` blocks project/local settings and Skill changes while the
  runtime supervisor session is active.
- `SubagentStart` and `SubagentStop` record minimal lifecycle events for
  `specialist-worker`.
- `SessionEnd` records the end of a runtime supervisor session.

The transitional local hook event files are not the authoritative audit store
and must not contain prompts, tool inputs, tool outputs, credentials, or
assistant messages. Durable runtime observability remains a later C.14 step.

## C.14.6 Process Session Runner

`SubprocessClaudeSessionRunner` is the concrete bounded process host for one
Claude session. It owns subprocess creation, project-root enforcement, JSON
envelope decoding, controlled non-zero failures, timeout/cancellation cleanup,
and best-effort process-tree termination.

C.14.6 deliberately does not choose the model provider or launcher command.
The command is supplied through `ClaudeProcessCommandBuilder`. Production
scheduler/bootstrap wiring remains on the legacy bridge until C.14.7 provides
and validates the Ollama-backed command builder.

Do not claim that production monitoring is Claude-native merely because the
process runner exists.
