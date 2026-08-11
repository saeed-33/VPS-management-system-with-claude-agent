# AI VPS Management - Claude Code Instructions

## Role

Claude Code is the primary supervisory orchestration runtime for this project.
It coordinates the fixed operational workflow and invokes project-owned tools
when they become available.

Claude Code does not replace Python services, PostgreSQL, RAG, SSH execution,
Policy, Evidence, Specialist definitions, or Ollama clients.

## Current transition phase

The project is in:

```text
Phase C - Claude Code Supervisory Runtime Transition
```

C.1 is structure-only. These instructions define boundaries and responsibilities
without changing production monitoring behavior.

## Fixed workflow

This workflow is mandatory:

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

Do not skip retrieval, analysis, Specialist execution, evidence grounding,
policy checks, persistence, sandbox validation, or approval gates.

## Responsibility split

```text
Claude Code
  = high-level supervision and orchestration

Python application
  = execution, persistence, safety, policy, evidence, RAG, SSH, Admin/API

PostgreSQL
  = source of truth

Ollama
  = operational LLM provider for analysis and specialist reasoning

MCP / controlled project tools
  = boundary between Claude Code and application capabilities
```

## LLM provider

Ollama is the project LLM provider for:

```text
report analysis
assisted RAG analysis
specialist reasoning
final synthesis
```

Do not bypass project LLM clients for these responsibilities. When tools exist,
call project tools that route LLM work through the configured Ollama clients.

## Safety invariants

Claude Code may request operations; Python authorizes them.

Never introduce or use normal-operation shortcuts that bypass:

```text
DiagnosticToolRegistry
DiagnosticPolicyEngine
Evidence validation
SpecialistDefinition permissions
budget enforcement
PostgreSQL persistence
Ollama project clients
sandbox remediation validation
user approval when policy requires it
```

Forbidden as normal agent capabilities:

```text
unrestricted shell
raw production SSH
raw production SQL
write-capable production remediation without policy approval
hard-coded domain Specialists as source of truth
```

## Current implementation references

Read these before changing transition behavior:

```text
docs/PROJECT_STATUS.md
docs/decisions/ADR-017-claude-code-supervisory-agent-runtime.md
docs/roadmap/claude-code-supervisory-transition-plan.md
docs/architecture/overview.md
docs/workflows/current-workflows.md
docs/operations/configuration.md
```

## Development rule

Preserve existing behavior unless an implementation step explicitly changes it
and includes tests. The current Python/LangGraph path remains available until
Claude-supervised execution passes equivalence and safety gates.
