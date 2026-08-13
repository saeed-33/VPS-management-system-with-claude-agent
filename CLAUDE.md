# AI VPS Management — Claude Code Runtime Contract

## Current gate state

The runtime program is the **C.14 - Real Claude-Native Orchestration** track,
now accepted through C.14.12; this document records the post-readiness current
state rather than a pending implementation plan.

```text
Phase 4.20: COMPLETE
C.14.0-C.14.11: COMPLETE
C.14.11A: PASS
C.14.12: PASS
C.14.13: PASS
C.14.14: PASS
Phase C: COMPLETE / CLOSED
Phase 5: COMPLETE / CLOSED
Phase 6: IMPLEMENTED / NOT CLOSED
automatic_remediation_allowed: false
```

## Responsibility split

```text
Claude Code
  = supervisory reasoning, sequencing, branching, and synthesis

Ollama
  = operational LLM provider for project-owned analysis/reasoning clients

MCP
  = bounded Claude-facing project capability surface

Python application
  = deterministic execution, validation, persistence, policy, evidence,
    budgets, SSH safety, database access, and Admin/API
```

Core rule:

```text
Claude decides WHAT / NEXT.
Python decides WHETHER ALLOWED and HOW IT IS EXECUTED SAFELY.
```

## Canonical architecture

```text
app/core             contracts, configuration, policy
app/capabilities     monitoring, analysis, investigation, knowledge
app/runtime/claude  native Claude CLI, AgentJobs, observability
app/interfaces       Admin HTTP/Web and vps MCP
app/infrastructure   PostgreSQL, known-hosts SSH, Ollama
app/composition      dependency wiring and bootstrap
```

Do not recreate the removed historical trees `app/domain`, `app/admin`,
`app/mcp`, `app/shared`, or `app/tools`.
Do not recreate `.claude/commands/` as a duplicate workflow surface.

## Fixed operational workflow

```text
periodic monitoring
 -> Claude Code supervisory session
 -> Ollama model
 -> vps MCP
 -> monitoring capability
 -> persisted report
 -> exact/similar historical analysis
 -> persisted analysis
 -> optional investigation
 -> dynamic DB-defined Specialists
 -> Evidence
 -> Final Diagnosis
 -> bounded remediation proposal
 -> Claude-native isolated sandbox validation
 -> fingerprint-bound approval gate
```

Do not fabricate current operational facts from historical incidents or
Knowledge RAG. Current claims require current reports or persisted Evidence.

## Agents and Skills

Agents:

```text
.claude/agents/server-supervisor.md
.claude/agents/specialist-worker.md
```

Skills:

```text
.claude/skills/monitor-server/SKILL.md
.claude/skills/analyze-incident/SKILL.md
.claude/skills/investigate-incident/SKILL.md
.claude/skills/plan-remediation/SKILL.md
```

`server-supervisor` is the main per-server coordinator and may invoke bounded
project tools. `specialist-worker` is a bounded worker and cannot delegate.
Domain-specific Specialist truth remains DB-defined and managed through the
project services, not hard-coded agent files.

## MCP and permissions

`.mcp.json` registers the `vps` server through
`tools/run_project_mcp_server.py`. The project surface contains exactly 25
tools. Calls are schema-validated, registered, policy-gated, budgeted, and
structured.

Claude must not use raw SSH, raw SQL, arbitrary shell, unrestricted filesystem
writes, generic subprocess execution, direct database writes, or any bypass of
the DiagnosticToolRegistry, DiagnosticPolicyEngine, Specialist permissions,
budgets, or Evidence validation.

Do not use `--dangerously-skip-permissions`. It is not an accepted runtime
method. Production remediation is not authorized while
`automatic_remediation_allowed` is `false`.

## Evidence and safety

Evidence IDs, report IDs, investigation IDs, claim IDs, conflict IDs, and
remediation IDs must come from project services. Unknown or foreign Evidence
references fail closed. Conflicts remain explicit. Policy DENY results must not
expose executable commands. SSH must use the configured private key and
`known_hosts`; command and connection timeouts remain bounded.

## Runtime observability

Every supervisory run is represented by an AgentJob with Claude session,
status, turns, tool calls, MCP state, duration, usage, and failure metadata.
Runtime snapshots persist report, analysis, investigation, Specialist, Evidence,
conflict, and diagnosis state. Application startup recovers interrupted jobs
into a deterministic failed state.

## Required references

Read the current canonical documents before changing runtime behavior:

```text
docs/PROJECT_STATUS.md
docs/architecture/overview.md
docs/operations/configuration.md
docs/operations/claude-runtime.md
docs/testing/TESTING_STRATEGY.md
docs/architecture/c14-12-runtime-readiness-gate.md
```

Phase 5 is complete and closed. Phase 6 is implemented but not closed until
its real native-sandbox acceptance gate passes. Keep
`automatic_remediation_allowed` false.
