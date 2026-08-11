# Current Architecture

<!-- DOC-STATUS: CURRENT -->

## Current project state

Phase 4 — Hierarchical Multi-Agent Investigation and Production Readiness — is complete.

```text
Operational readiness: ready_for_supervised_operations
Automatic remediation: false
```

The accepted Phase 4.20 readiness run measured:

```text
10 persisted runtime snapshots
30 controlled routing/provider/policy observations
80 aggregate observations
all 8 readiness metrics passed
```

Reference automated regression reference immediately before documentation closeout:

```text
237 passed, 1 warning
```

The warning is the existing Starlette/TestClient deprecation warning.

## End-to-end architecture

```text
Admin / Web UI
      |
FastAPI API
      |
Shared Services / Repositories
      |
MonitoringScheduler
      |
MonitoringService
      |
SSH monitoring commands
      |
Monitoring Report
      |
AnalysisAgentManager
      |
AnalysisOrchestrator
      +--> normalization / fingerprint
      +--> analysis reuse policy
      +--> Incident RAG
      +--> LLM analysis
      +--> retrieval indexing
      |
Initial Analysis
      |
InvestigationRouter
      |
Investigation Persistence
      |
SpecialistRegistry
      |
Claude Investigation Coordinator
      |
Selected Dynamic Specialists
      |
SpecialistContextBuilder
      +--> Initial Analysis
      +--> accumulated Evidence
      +--> Incident RAG
      +--> Knowledge RAG
      +--> Specialist instructions
      |
SpecialistReasoningAgent
      |
Diagnostic Tool Requests
      |
DiagnosticToolRegistry
      |
DiagnosticPolicyEngine
      |
EvidenceCollectionService
      |
Known read-only SSH implementations
      |
SpecialistInvestigationLoop
      |
parallel / secondary Specialist waves
      |
CrossSpecialistCorrelator
      |
confirmed / probable / unknown claims
      |
FinalDiagnosis
      |
FinalDiagnosisSynthesizer
      |
Runtime Snapshot Persistence
      |
Investigation Read Service
      |
Investigation API + Administration UI
      |
Persisted Runtime Evaluation
      |
Safety / Failure Injection Evaluation
      |
Production Readiness Gate
```

## Dynamic Specialists

Specialists are persisted operator-managed data, not hard-coded Python classes.

Runtime definitions include:

```text
slug
name
description
instructions
domains
trigger_hints
knowledge_topics
allowed_tool_ids
priority
max_rounds
max_actions
```

Only enabled validated definitions appear in the Specialist Registry.

Claude reads and runs Specialists through controlled MCP tools:

```text
get_available_specialists
get_specialist_definition
run_specialist
```

These tools still use the DB-backed `SpecialistRegistry` as the source of truth.
`run_specialist` accepts only Specialists selected by the persisted
Investigation routing decision, then passes the runtime definition to the
existing Specialist loop. The loop remains responsible for enforcing
`allowed_tool_ids`, Specialist budgets, Investigation budgets, diagnostic
policy, Evidence collection, and Ollama-backed Specialist reasoning.

`.claude/agents/generic-specialist.md` is a generic role description only. It is
not a domain Specialist registry and must not duplicate Admin-managed
Specialist definitions.

`ClaudeMultiSpecialistSupervisor` coordinates multiple selected Specialists
sequentially through the same MCP boundary. It records an `agent_jobs` entry,
applies supervisor-level limits for max Specialists, max turns, max tool calls,
and timeout, then collects structured run summaries. It does not pass one
Specialist's private runtime state directly into another Specialist; shared
state must flow through persisted Investigation/Evidence read models and
project tools.

## Routing

`InvestigationRouter` is deterministic and conservative.

It decides:

```text
should_investigate
detected_domains
runtime_specialists
selected_specialists
unmatched_issue_indexes
```

Healthy/no-issue analysis does not open an Investigation merely because Specialists exist.

## Dual RAG architecture

Incident RAG and Knowledge RAG remain separate.

Incident RAG retrieves similar historical monitoring incidents. Historical incidents are context, not proof of current server state.

Knowledge RAG retrieves attributed technical-documentation chunks. Technical Knowledge may explain behavior but cannot establish a live operational fact without Evidence.

## Specialist context and provenance

Each Specialist receives a bounded context assembled from:

```text
task
Specialist definition/instructions
Initial Analysis
current Evidence
Incident RAG
Knowledge RAG
```

Evidence and Knowledge references retain stable IDs. Any model output that cites an unknown Evidence or Knowledge ID is rejected.

## Diagnostic execution boundary

The model never receives arbitrary shell capability.

```text
LLM structured Tool request
 -> registered Diagnostic Tool
 -> typed arguments
 -> Diagnostic Policy
 -> ALLOW / DENY
 -> approved execution envelope
 -> known read-only SSH implementation
 -> EvidenceReference
```

DENY results never produce an executable command.

Budgets exist at Specialist and Investigation scope.

## Claude-Supervised Orchestration

Claude owns high-level supervisory orchestration, not domain authority.

It coordinates:

```text
Specialist execution
worker quotas
aggregation
secondary Specialist waves
bounded termination
```

Project-owned services continue to own:

```text
database
repositories
RAG
Registry
Policy
Evidence
SSH execution
correlation contracts
Final Diagnosis
persistence
```

## Correlation and Final Diagnosis

Specialist findings are correlated at server scope.

Claims are classified as:

```text
confirmed
probable
unknown
```

Conflicting states remain explicit. A conflict cannot be silently resolved by narrative generation.

Final narrative synthesis may only narrate validated diagnosis objects and their known Claim/Conflict IDs.

## Persistence and read model

Investigation routing is persisted before runtime execution.

After runtime, the snapshot persists:

```text
status
orchestrator / execution mode
Specialist runs
actions used
Evidence
correlated claims
conflicts
Final Diagnosis
narrative
```

The read service exposes this through API and read-only administration pages.

## Evaluation and readiness

Phase 4.20 introduced a separate evaluation layer.

Measured metrics:

```text
routing_recall
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
provider_resilience
policy_safety
```

Hard safety metrics require 100% pass rate and fail closed.

The current accepted gate state is:

```text
ready_for_supervised_operations
```

## Current boundary

The project is ready for supervised diagnostic operations.

Not authorized yet:

```text
automatic restart
kill process
configuration modification
package installation
reboot
firewall modification
arbitrary shell
automatic remediation
```

Phase C.10 introduces supervised Remediation Plan, approval request, sandbox
result, risk classification, audit trail, before/after Evidence IDs, and
rollback expectation records. It does not grant write-capable production
authority.

Claude may use these controlled remediation MCP tools:

```text
propose_remediation
create_remediation_plan
test_remediation_in_sandbox
get_sandbox_result
request_user_approval
apply_approved_remediation
```

`apply_approved_remediation` remains policy-gated. Failed sandbox validation,
missing sandbox validation, missing required approval, or
`automatic_remediation_allowed = false` blocks production application.

## Orchestration readiness Gate

`RuntimeReadinessGate` validates Claude-supervised orchestration against
the required Phase C acceptance matrix.

The required matrix covers operational diagnosis, Specialist coordination,
provider/runtime failures, policy denial, and remediation sandbox/approval
cases. Any critical failure in safety, grounding, policy, fixed workflow order,
budget behavior, conflict preservation, final diagnosis grounding, or sandbox
validation blocks Claude orchestration until the failure is resolved.

Latency, tool-call count, and cost are recorded for review. They are not allowed
to override a safety or policy failure.

## Claude Supervisor

`ClaudeSupervisor` is the C.12 scheduler-facing runtime boundary. The scheduler
submits server monitoring work to the Claude monitoring cycle through this
boundary.

Scheduler iterations delegate to `ClaudeSupervisedMonitoringCycle`; that cycle
invokes project-owned MCP tools and existing services for monitoring, analysis,
investigation, Specialists, remediation planning, persistence, policy, and
Ollama-backed LLM reasoning.

The `/health` endpoint exposes the active Claude supervisor status.

## Claude Code Runtime

ADR-017 defines Claude Code as the supervisory orchestration runtime.

The target responsibility split is:

```text
Claude Code
  = high-level supervisory orchestration

Python services
  = execution, persistence, policy, evidence, RAG, SSH, Admin/API

Ollama
  = operational LLM provider for report analysis, specialist reasoning,
    assisted RAG analysis, and final synthesis
```

The fixed workflow is:

```text
periodic monitoring
 -> per-server subordinate agent
 -> exact/similar historical report lookup
 -> exact match: reuse previous analysis
 -> similar match: pass top 3 similar reports to the LLM
 -> Ollama-backed initial analysis
 -> Specialist selection and deeper analysis when issues exist
 -> final diagnosis
 -> remediation proposal
 -> isolated-environment validation
 -> policy/user-gated production application
```

Claude Code must not bypass project-owned retrieval, Ollama clients, policy,
evidence, persistence, budget enforcement, or sandbox validation.

## Claude Runtime Adapter

Phase C.2 adds a project-owned runtime adapter under `app/runtime/claude/`.

Its current responsibility is bounded Claude session execution:

```text
ClaudeRuntimeRequest
 -> ClaudeSessionRunner
 -> timeout boundary
 -> structured JSON result parser
 -> ClaudeRuntimeResult
```

The adapter captures:

```text
session_id
status
structured_output
error_code / error_message
turn_count
tool_call_count
usage_metadata
```

C.2 does not expose operational MCP tools. Requests that include operational
tools are rejected while tool access remains disabled. Persistence of agent jobs
starts in C.3.

## Claude Agent Job Persistence

Phase C.3 adds `agent_jobs` as the audit and recovery record for Claude
supervisory runtime work.

The persisted record tracks:

```text
job_id
job_type
server_id
status
claude_session_id
started_at / completed_at
error_code / error_message
turn_count
tool_call_count
usage_metadata
metadata
```

`ClaudeAgentJobService` maps `ClaudeRuntimeRequest` and `ClaudeRuntimeResult`
objects into `AgentJobModel` records through `AgentJobRepository`.

On application restart, queued or running jobs are recoverable into a
deterministic failed state:

```text
error_code = interrupted_after_restart
status = failed
```

C.3 does not expose MCP tools and does not change production monitoring
behavior.

## Project Tool Boundary

The controlled project-tool execution boundary lives under `app/tools/`.
`app/mcp/` provides schemas, serializers, and compatibility exports for Claude
tool calls.

The initial tool set is deliberately small:

```text
get_server_context
get_monitoring_profile
run_monitoring
get_report
get_latest_report
```

The boundary calls existing services:

```text
ProjectToolCall
 -> ProjectMcpToolBoundary
 -> app/tools project boundary
 -> ServerService / MonitoringProfileService / MonitoringService / ReportQueryService
 -> ProjectToolResult
```

It provides:

```text
tool inventory
input schemas
input validation
structured success results
normalized error results
unknown-tool rejection
```

It does not expose:

```text
raw SSH
raw SQL
arbitrary shell
filesystem write
remediation tools
external MCP server
```

The external MCP serving layer is intentionally deferred. C.4 only establishes
and tests the internal contract boundary that later runtime integration will
use.

## Claude-Supervised Monitoring Cycle

Phase C.5 adds `ClaudeSupervisedMonitoringCycle`:

```text
ClaudeSupervisedMonitoringCycle
 -> create agent job
 -> mark job running
 -> get_server_context
 -> get_monitoring_profile
 -> run_monitoring
 -> get_latest_report
 -> complete agent job
```

The service uses only the controlled `ProjectMcpToolBoundary`; it does not use
raw SSH, raw SQL, arbitrary shell, or remediation tools.

Failure behavior is fail-closed:

```text
any required tool failure
 -> stop cycle
 -> persist ClaudeRuntimeResult(status=failed)
 -> return ClaudeMonitoringCycleResult(status=failed)
```

C.5 does not add an external Claude CLI runner or external MCP server. It
establishes the first project-owned execution path that later Claude runtime
integration can drive.

## Analysis and Retrieval Tool Boundary

Phase C.6 extends `ProjectMcpToolBoundary` with analysis and retrieval tools:

```text
find_exact_report_match
search_similar_incidents
get_top_similar_reports
analyze_report
get_analysis
search_knowledge
```

These tools preserve the fixed workflow:

```text
monitoring report
 -> exact historical report match lookup
 -> exact match: reusable analysis
 -> otherwise top 3 similar incident reports
 -> AnalysisOrchestrator
 -> Ollama-backed analysis through project clients when LLM is enabled
```

Implementation boundaries:

```text
ReportNormalizer and ReportFingerprintService compute exact-match keys
AnalysisRepository owns exact match and persisted analysis reads
HybridRetriever/RagRetriever owns similar incident retrieval
KnowledgeHybridRetriever owns Knowledge RAG
AnalysisOrchestrator owns report analysis and LLM provider behavior
```

Claude Code does not receive embeddings, pgvector, FTS, raw retrieval tables, or
direct Ollama access. It receives structured tool results from project-owned
services.

## Investigation Tool Boundary

Phase C.7 extends `ProjectMcpToolBoundary` with high-level investigation tools:

```text
start_investigation
get_investigation
get_investigation_status
get_evidence
```

The write boundary is intentionally narrow:

```text
start_investigation
 -> get persisted report
 -> get persisted analysis
 -> InvestigationRouter.route()
 -> InvestigationPersistenceService.persist_routing_decision()
 -> InvestigationReadService.get()
```

Runtime execution is not moved into Claude at this step. C.7 only proves that
Claude-facing tooling can start and inspect the existing investigation state
machine through project services.

Evidence access is read-only:

```text
get_evidence
 -> InvestigationReadService
 -> persisted runtime_snapshot.evidence
```

Claude Code cannot fabricate investigation state or Evidence IDs through these
tools.

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
