# Project Status

<!-- DOC-STATUS: CURRENT -->

Last synchronized project milestone: **Phase 4.20 complete**.

## Operational status

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

## Accepted readiness evidence

```text
runtime snapshots: 10
persisted runtime observations: 50
controlled safety observations: 30
aggregate observations: 80
readiness metrics passed: 8/8
```

## Accepted metrics

```text
routing_recall              PASS
specialist_completion       PASS
evidence_grounding          PASS
budget_compliance           PASS
conflict_preservation       PASS
final_diagnosis_grounding   PASS
provider_resilience         PASS
policy_safety               PASS
```

## Current product boundary

Implemented:

```text
monitoring
analysis
Incident RAG
Knowledge RAG
dynamic Specialists
deterministic routing
Claude-supervised orchestration
read-only diagnostic tools
Policy
Evidence
cross-Specialist correlation
Final Diagnosis
runtime persistence
Investigation API/UI
evaluation and safety gate
```

Not implemented/authorized:

```text
automatic remediation
write-capable remediation tools
approval workflow
rollback workflow
```

## Claude Runtime Architecture

ADR-017 defines **Claude Code as the supervisory orchestration runtime**.

Python services remain authoritative for monitoring tools, analysis tools,
Incident RAG, Knowledge RAG, dynamic Specialists, SSH execution, persistence,
policy, evidence, and the Admin/API control plane.

## Fixed operational workflow

Claude Code must preserve this workflow order:

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

The workflow is fixed. Claude Code may coordinate decisions inside this path,
but must not skip or replace the project-owned retrieval, policy, evidence,
persistence, or sandbox validation boundaries.

## LLM provider

Ollama is the operational LLM provider for project analysis and specialist
reasoning. Claude Code supervises orchestration and must invoke project tools
that use the configured Ollama clients instead of bypassing them.

## Next phase

**Phase C - Claude Code Supervisory Runtime.**

Implementation plan:

`docs/roadmap/claude-runtime-implementation-plan.md`

Current Phase C progress:

```text
C.0 Documentation and architectural freeze: complete
C.1 Claude Code project structure: complete
C.2 Claude Runtime Adapter: complete
C.3 Agent Job Persistence and Observability: complete
C.4 Project MCP Boundary: complete
C.5 First Claude-supervised Monitoring Cycle: complete
C.6 Analysis and Retrieval Tools: complete
C.7 Claude-supervised Investigation: complete
C.8 Dynamic Specialist Integration: complete
C.9 Multi-Specialist Supervision: complete
C.10 Remediation Proposal and Sandbox Validation: complete
C.11 Runtime Readiness Evaluation: complete
C.12 Claude Supervisor Runtime Boundary: complete
C.13 Remove Duplicated Control Flow: complete
R.1 Runtime Package Boundary: complete
R.2 Tool Package Boundary: complete
R.3 Domain Services Boundary: complete
R.4 Admin Surface Alignment: complete
R.5 Documentation and Tests: complete
C.14 Real Claude-Native Orchestration: in progress
```

C.1 added the project-level Claude Code instruction structure only. It did not
change production monitoring, analysis, investigation, or remediation behavior.

C.2 added a project-owned Claude runtime adapter with bounded execution,
structured-result parsing, timeout handling, controlled failure results, and
tool-access blocking for this phase. It does not expose operational MCP tools
or change production monitoring behavior.

C.3 added persistent `agent_jobs` records, repository/service APIs, recovery of
queued/running jobs after restart into an auditable failed state, and tests for
job creation, completion, filtering, and recovery. It does not expose
operational MCP tools or change production monitoring behavior.

C.4 added the first controlled project tool boundary for Claude-facing
capabilities: `get_server_context`, `get_monitoring_profile`, `run_monitoring`,
`get_report`, and `get_latest_report`. These tools call existing project
services, normalize errors, expose schemas, and reject unknown tools. This is an
internal boundary only; no external MCP server is exposed yet.

C.5 added the first Claude-supervised monitoring cycle service. It records an
agent job, follows the fixed tool order, invokes the controlled project tool
boundary, persists a controlled runtime result, and stops with an auditable
failure if any required tool fails. It does not introduce an external Claude CLI
runner or external MCP server yet.

C.6 added controlled analysis and retrieval tools: exact report match lookup,
top-3 similar incident retrieval, report analysis through `AnalysisOrchestrator`,
persisted analysis reads, and Knowledge RAG search. These tools reuse existing
Python services and keep Ollama calls behind project analysis/specialist
clients. Missing optional LLM/RAG dependencies return controlled errors.

C.7 added controlled high-level investigation tools: `start_investigation`,
`get_investigation`, `get_investigation_status`, and `get_evidence`. Starting
an investigation uses the existing `InvestigationRouter` and
`InvestigationPersistenceService`, then exposes read models through
`InvestigationReadService`. It does not run Specialist runtime loops yet.

C.8 added dynamic Specialist MCP tools: `get_available_specialists`,
`get_specialist_definition`, and `run_specialist`. Specialist definitions still
come from the DB-backed `SpecialistRegistry`; disabled or unselected
Specialists are rejected; `allowed_tool_ids` and per-Specialist budgets remain
enforced by the existing Specialist runtime loop. Specialist LLM reasoning stays
behind the configured Ollama-backed project clients.

C.9 added `ClaudeMultiSpecialistSupervisor`, a sequential Claude-supervised
coordination layer over selected DB-defined Specialists. It records an
`agent_jobs` runtime job, reads the persisted Investigation, runs selected
Specialists through controlled MCP tools, enforces supervisor-level limits for
max Specialists, max turns, max tool calls, and timeout, then returns structured
run summaries without sharing Specialist-local state outside the persisted
Investigation/tool boundary.

C.10 added supervised remediation contracts, persistence, and controlled MCP
tools: `propose_remediation`, `create_remediation_plan`,
`test_remediation_in_sandbox`, `get_sandbox_result`,
`request_user_approval`, and `apply_approved_remediation`. Plans must link to
diagnosis claims and Evidence, sandbox results are persisted, failed sandbox
validation blocks production application, high-risk actions request user
approval, and project policy still denies production remediation because
`automatic_remediation_allowed` remains false.

C.11 added `RuntimeReadinessGate`, a deterministic acceptance gate that
compares required acceptance observations across the Phase C matrix. Critical
failures in safety, grounding, policy, fixed workflow order, budget behavior,
conflict preservation, final diagnosis grounding, or sandbox validation block
Claude orchestration. Latency, tool calls, and cost regressions are recorded
for review but do not by themselves authorize or block the safety decision.

C.12 added the Claude supervisor used by scheduled monitoring. The scheduler
calls the Claude monitoring cycle through this supervisor, and `/health`
exposes the active supervisor status.

C.13 sets future orchestration development around Claude-supervised runtime
coordination, while project-owned operational services remain authoritative and
reusable.

R.1 moved Claude runtime code under `app/runtime/claude/` and kept
`ClaudeSupervisor` as the scheduler-facing runtime entrypoint.

R.2 moved the project tool execution boundary under `app/tools/`, added a
tool catalog with monitoring, reports, retrieval, investigation, specialists,
and remediation groups, and kept MCP as a thin schema/compatibility boundary.

R.3 moved Knowledge RAG domain code under `app/domain/knowledge/`, kept
knowledge ingestion, chunking, source loading, and retrieval callable from
tools and tests, and added a domain boundary test that prevents domain modules
from importing runtime or MCP adapters.

R.4 added the operator-facing system runtime surface. `/api/system/runtime`
returns supervisor status and the grouped project tool catalog, while `/system`
renders that state in the admin UI. The admin layer reads runtime/tool metadata
only and does not encode supervisory workflow order or branch decisions.

R.5 added documentation contract coverage for the runtime guides, generated
project structure, and generated test catalog. It also aligns the Claude runtime
operations guide with the configured Ollama defaults.

C.14 starts the correction that connects Claude Code to project tools directly.
The project now registers a `vps` MCP server in `.mcp.json`, exposes project
tools through a stdio MCP protocol server, and defines Claude subagents with
frontmatter, allowed MCP tools, skills, and turn budgets.

Phase 5 - Supervised Remediation follows after Phase C unless a later ADR
changes this ordering.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
