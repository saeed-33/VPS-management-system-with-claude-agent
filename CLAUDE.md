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

Agent files remain transitional until C.14.3. The operational skills are
accepted as contracts, but they are not proof that a real Claude session is
already executing the production workflow.

Before Phase 5, C.14 must still implement and prove:

```text
bounded final agent contracts
least-privilege tools and model inheritance
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
