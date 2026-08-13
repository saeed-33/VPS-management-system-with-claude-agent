# Current Architecture Overview

<!-- DOC-STATUS: CURRENT -->

This document describes the implemented Phase C and Phase 5 system. The
current gate state is Phase 4.20 complete, C.14.11A pass, C.14.12 pass,
C.14.13 pass, and C.14.14 pass. Phase C is closed; Phase 5 is implemented but
not closed because real safe-target acceptance is unavailable.

## Responsibility invariant

```text
Claude decides WHAT / NEXT.
Python decides WHETHER ALLOWED and HOW IT IS EXECUTED SAFELY.
```

Claude Code provides supervisory reasoning, sequencing, branching, and
synthesis. Python remains authoritative for capabilities, validation, policy,
budgets, evidence, persistence, SSH, database access, and safety boundaries.
Ollama is the operational LLM provider; no OpenAI, LangGraph, or Anthropic-hosted
reasoning model is part of the active runtime contract.

## Canonical package layout

```text
app/
├── core/
│   ├── contracts/       provider-independent contracts and DTOs
│   ├── policies/        fail-closed diagnostic policy
│   └── config.py        environment-backed settings
├── capabilities/
│   ├── monitoring/      monitoring profiles, commands, and reports
│   ├── analysis/        normalization, retrieval, and Ollama analysis
│   ├── investigation/   routing, Specialists, Evidence, and diagnosis
│   └── knowledge/       technical knowledge ingestion and retrieval
├── runtime/claude/      native Claude CLI, jobs, sessions, and observability
├── interfaces/
│   ├── admin/           FastAPI/Admin web and API adapters
│   └── mcp/             bounded project MCP registry and protocol server
├── infrastructure/
│   ├── database/        PostgreSQL models, repositories, and engine
│   ├── ssh/             known-hosts SSH and bounded command execution
│   └── llm/ollama/      Ollama provider implementations
└── composition/         dependency container and application wiring
```

The removed historical production trees are `app/domain`, `app/admin`,
`app/mcp`, `app/shared`, and `app/tools`. They must not be recreated.

## Runtime sequence

```text
Scheduler / periodic monitoring
        ↓
ClaudeSupervisor
        ↓
native Claude Code CLI
        ↓
Ollama-backed model
        ↓
vps MCP server
        ↓
monitoring capability and persisted Report
        ↓
exact reuse or similar historical retrieval
        ↓
persisted Analysis
        ↓
optional InvestigationRouter decision
        ↓
DB-defined Specialist definitions and bounded runs
        ↓
Evidence collection and validation
        ↓
correlation, conflicts, and Final Diagnosis
        ↓
bounded remediation proposal only
```

An accepted real runtime session persists an `AgentJob`, Claude session
observability, report, analysis, and, when requested by routing, investigation
and Specialist runtime state. A connection failure remains an explicit failure
outcome; it is never converted into a fabricated healthy result.

## Layer responsibilities

### Claude Code

Claude is the supervisory runtime. `server-supervisor` is the main per-server
agent contract. `specialist-worker` is a bounded worker contract and cannot
delegate further. Claude selects the next allowed project-tool operation, but
does not own domain truth or safety authorization.

### Ollama

Ollama provides operational report analysis, Specialist reasoning, retrieval
assistance, and final synthesis through project-owned clients. The configured
provider is restricted to `ollama`, and the Claude runtime routes through the
configured Ollama-compatible transport.

### MCP

`.mcp.json` starts `tools/run_project_mcp_server.py` as the `vps` server. The
server exposes exactly 25 project tools from `app/interfaces/mcp/`. Tool
schemas, registration, validation, structured errors, and invocation remain
project-owned. MCP does not expose raw SSH, raw SQL, arbitrary shell,
unrestricted filesystem writes, or generic subprocess execution.

### Python capabilities

Python implements monitoring, report and analysis persistence, exact/similar
retrieval, deterministic routing, DB-defined Specialist execution, Evidence
collection, correlation, final diagnosis objects, AgentJob persistence, Admin
API/web adapters, and all policy and budget checks.

### Policy and safety boundary

Diagnostic requests pass through registered tools and the
`DiagnosticPolicyEngine`. Denials do not return executable commands. SSH uses
validated private keys and `known_hosts`; command and connection timeouts are
bounded. Unknown MCP tools, invalid arguments, unowned Evidence references,
provider failures, missing approval, and budget exhaustion fail closed.

### Evidence grounding

Current operational claims require current reports or persisted Evidence.
Evidence IDs and ownership metadata are validated before use. Historical
incidents and Knowledge RAG provide context, not proof of current server state.
Conflicting claims remain explicit rather than being silently resolved by
narrative generation.

### Database persistence and observability

PostgreSQL is the source of truth for servers, monitoring profiles, commands,
reports, analyses, Specialist definitions, investigations, runtime snapshots,
Evidence, and AgentJobs. The observability projection records Claude session,
tool-call, MCP, duration, and failure state. Startup recovery marks interrupted
queued/running jobs as failed with `interrupted_after_restart`.

## Bounded autonomy

The current system is ready for supervised diagnostic operations and the
implemented Phase 5/6 remediation workflow remains explicitly bounded:
`automatic_remediation_allowed` is `false`, production writes are not
authorized, and Phase 6 cannot request approval until native sandbox
attestation and safe-target validation pass.

## Related canonical documents

- [Current project status](../PROJECT_STATUS.md)
- [Current workflows](../workflows/current-workflows.md)
- [Claude runtime operations](../operations/claude-runtime.md)
- [Runtime configuration](../operations/configuration.md)
- [C.14.12 readiness gate](c14-12-runtime-readiness-gate.md)
- [Phase C closeout](../roadmap/phase-c-closeout.md)

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
