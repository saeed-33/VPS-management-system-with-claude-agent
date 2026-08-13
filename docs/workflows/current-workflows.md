# Current Operational Workflows

<!-- DOC-STATUS: CURRENT -->

## Monitoring to diagnosis

```text
periodic monitoring
 -> Claude Code supervisory session
 -> Ollama-backed model
 -> vps MCP
 -> monitoring capability
 -> persisted Monitoring Report
 -> exact historical match or similar historical retrieval
 -> persisted Analysis
 -> optional Investigation routing
 -> dynamic DB-defined Specialists
 -> Evidence collection
 -> correlation and Final Diagnosis
 -> bounded remediation proposal only
```

Claude chooses the next project-tool operation. Python services remain
authoritative for execution, persistence, validation, policy, budgets, and
Evidence.

## Analysis and retrieval

An exact normalized report match may reuse a persisted Analysis. Otherwise the
application retrieves bounded similar incidents and Knowledge RAG context, then
uses the configured Ollama client for a structured Analysis. Historical context
is never treated as proof of current server state.

## Investigation and Specialists

```text
Report + Analysis
 -> InvestigationRouter
 -> persist should_investigate and selected DB Specialists
 -> Claude invokes bounded MCP tools
 -> Specialist worker receives DB definition, task, context, Evidence, and budgets
 -> DiagnosticPolicyEngine
 -> known-hosts SSH diagnostic execution
 -> Evidence
 -> correlation, conflict preservation, and Final Diagnosis
```

Healthy/no-issue analyses do not create unnecessary investigations. Specialist
definitions are database-managed; domain-specific Claude agent files are not
the source of truth.

## Persistence and observability

Reports, analyses, investigations, runtime snapshots, Evidence, Specialist
runs, and AgentJobs are persisted in PostgreSQL. AgentJob observability records
session, tool-call, MCP, duration, and failure metadata. Startup recovery marks
interrupted queued/running jobs failed instead of leaving them active.

## Safety boundary

All diagnostic operations use registered project tools and policy checks. The
MCP surface does not expose raw SSH, raw SQL, arbitrary shell, unrestricted
filesystem writes, or generic subprocess execution. Evidence references are
validated and budgets are enforced. `automatic_remediation_allowed` remains
`false`.

## Phase 5 boundary

Phase C is closed at C.14.14. Phase 5 Supervised Remediation is the next
allowed phase but is not implemented here. The current workflow may produce a
bounded remediation proposal, but it does not perform production
restart, process termination, package change, configuration write, reboot,
firewall change, or arbitrary shell execution.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
