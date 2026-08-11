# Claude Code Supervisory Transition Plan

Status: **APPROVED FOR IMPLEMENTATION**

Date: **2026-08-11**

Related ADR: `docs/decisions/ADR-017-claude-code-supervisory-agent-runtime.md`

## Goal

Introduce Claude Code as the primary supervisory orchestration runtime without
replacing project functions already implemented and accepted through Phase
4.20.

The migration changes **orchestration ownership**, not domain capabilities.

Target state:

```text
Scheduler / Admin / API
      -> Claude Code Supervisor
      -> MCP / controlled project tools
      -> existing project services
      -> Monitoring / Analysis / RAG / Investigation / Specialists / SSH / DB
      -> Ollama when project LLM reasoning is required
```

## Fixed operational workflow

This transition must preserve one fixed workflow:

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

Claude Code may coordinate decisions inside this path, but it must not replace
or skip project-owned retrieval, policy, evidence, persistence, budget, or
sandbox-validation boundaries.

## LLM provider

Ollama is the operational LLM provider for report analysis, assisted RAG
analysis, specialist reasoning, and final synthesis.

Claude Code supervises orchestration. It must invoke project tools that route
LLM work through the existing Ollama clients instead of bypassing them.

## Non-goals

This transition does **not** authorize:

```text
rewriting the monitoring system inside Claude prompts
rewriting RAG inside Claude
direct arbitrary SSH from Claude
raw SQL access from Claude
moving Specialist definitions out of the database
removing Policy Engine
removing evidence/provenance validation
bypassing Ollama project clients for analysis/specialist reasoning
production remediation without policy/approval authorization
big-bang deletion of LangGraph or current orchestration
changing accepted Phase 4 behavior without explicit tests
```

## Migration strategy

The migration is intentionally incremental:

```text
CURRENT
  Python/LangGraph orchestration

DUAL PATH
  current path + Claude supervisory path

VALIDATION
  behavior + safety + persistence + Ollama comparison

TARGET
  Claude owns high-level coordination
  Python services remain authoritative capabilities
```

No existing orchestration code is removed until the replacement path has passed
acceptance.

---

# Transition Phase C - Claude Supervisory Runtime

This transition phase is inserted **before Phase 5 Supervised Remediation**.

## C.0 - Documentation and architectural freeze

Deliverables:

```text
ADR-017 accepted
this transition plan accepted
docs/PROJECT_STATUS.md updated to show Phase C as next
fixed operational workflow documented
Ollama documented as the operational LLM provider
existing Phase 4 behavior declared baseline for regression comparison
```

Acceptance:

```text
no runtime change
canonical docs agree on Phase C, fixed workflow, and Ollama
```

---

## C.1 - Claude Code project structure

Create the initial agent-control structure:

```text
CLAUDE.md
.mcp.json
.claude/
  settings.json
  rules/
    monitoring.md
    investigation.md
    specialists.md
    rag.md
    remediation.md
    safety.md
  commands/
    monitor.md
    analyze.md
    investigate.md
    diagnose.md
  skills/
  agents/
  hooks/
```

Important rule:

```text
These files define boundaries and responsibilities only.
They do not receive duplicated business logic from Python.
```

Acceptance:

```text
Claude Code loads project-level instructions
safety rules prohibit bypassing project services and policy
fixed operational workflow is stated as mandatory
Ollama is stated as the project LLM provider
no production monitoring behavior changes
```

---

## C.2 - Claude Runtime Adapter

Add a project-owned adapter for bounded Claude executions.

Suggested location:

```text
app/integrations/claude/
  __init__.py
  runtime.py
  models.py
  session.py
  result_parser.py
  exceptions.py
```

Responsibilities:

```text
start runtime job
provide task/context
configure allowed tools
set timeout
set max turns
capture session id
capture structured result
capture failure
capture usage metadata
cancel safely
```

Required runtime states:

```text
queued
running
completed
failed
timed_out
cancelled
```

Acceptance tests:

```text
simple bounded Claude invocation succeeds
timeout is enforced
failure is persisted/returned as a controlled result
invalid structured output is rejected
no operational tool access yet
```

---

## C.3 - Agent Job Persistence and Observability

Introduce persistent runtime records.

Minimum model:

```text
agent_jobs
  id
  job_type
  server_id
  status
  claude_session_id
  started_at
  completed_at
  error_code
  error_message
  turn_count
  tool_call_count
  usage_metadata
```

Exact schema must follow existing repository/model conventions.

Admin visibility should eventually expose:

```text
job
server
type
status
duration
session
tool calls
failure
```

Acceptance:

```text
job survives application restart
interrupted job has deterministic recovery state
failures are auditable
```

---

## C.4 - Project MCP Boundary

Expose a deliberately small first set of high-level existing project functions:

```text
get_server_context
get_monitoring_profile
run_monitoring
get_report
get_latest_report
```

The MCP implementation must call existing services rather than reimplementing
them.

Forbidden first-version tools:

```text
arbitrary_shell
raw_ssh
raw_sql
filesystem_write
remediation_write
```

Acceptance for each MCP tool:

```text
input schema validated
authorization/policy preserved
existing service invoked
same persisted result as direct application call
error normalized
audit/log entry available
```

---

## C.5 - First Claude-supervised Monitoring Cycle

First end-to-end milestone for one controlled server/profile:

```text
trigger
 -> Claude Supervisor
 -> get_server_context
 -> run existing monitoring function
 -> read resulting report
 -> return structured cycle result
```

Claude does not yet own deep investigation.

Comparison:

```text
A - current monitoring path
B - Claude-supervised path
```

Compare:

```text
executed monitoring profile
command execution semantics
report persistence
connection/error behavior
timestamps/status
auditability
```

Acceptance:

```text
no material behavior regression
```

---

## C.6 - Analysis and Retrieval Tools

Expose existing analysis and retrieval capabilities:

```text
find_exact_report_match
search_similar_incidents
get_top_similar_reports(limit=3)
analyze_report
get_analysis
search_knowledge
```

Rules:

```text
exact match reuses previous analysis
similar match passes at most the top 3 similar reports to the LLM context
embeddings, FTS, pgvector, RRF, filtering, and attribution stay in Python
LLM calls route through the configured Ollama clients
Claude cannot fabricate persisted source IDs
```

Acceptance:

```text
same report can be analyzed through the new path
exact reuse behavior matches current project policy
top-3 similar report context is bounded and traceable
retrieved sources are identical or explainably equivalent to direct service use
Ollama availability, timeout, and structured output behavior are tested
provenance IDs remain valid
```

---

## C.7 - Claude-supervised Investigation

Expose high-level investigation functions:

```text
start_investigation
get_investigation
get_investigation_status
get_evidence
```

Initially, the existing investigation implementation may still execute current
orchestration internally. This proves Claude can supervise investigation as a
project function before deeper orchestration ownership changes.

Acceptance:

```text
investigation is persisted exactly as before
current budgets remain enforced
evidence remains traceable
Claude cannot bypass the investigation state machine through MCP
```

---

## C.8 - Dynamic Specialist Integration

Expose dynamic Specialist capabilities:

```text
get_available_specialists
get_specialist_definition
run_specialist
```

Rules:

```text
SpecialistDefinition from DB is authoritative
enabled status is respected
allowed_tool_ids are respected
budgets are respected
specialist LLM reasoning routes through Ollama
generic Claude specialist role only
```

No hard-coded domain Specialist becomes source of truth under `.claude/agents/`.

Acceptance:

```text
changing a Specialist definition in the Admin UI changes the next run
no Python or .claude/agents change is needed for Specialist definition changes
```

---

## C.9 - Multi-Specialist Supervision

Claude Supervisor may coordinate several project-managed Specialist runs.

Target flow:

```text
report / initial diagnosis
 -> Claude Supervisor
 -> select DB-defined Specialists
 -> run Specialist tasks
 -> collect structured results
 -> request additional project functions if needed
 -> subordinate agent aggregation
 -> final coordination result
```

Parallel execution may be added only after state isolation is proven.

Required limits:

```text
max specialists
max turns
max tool calls
job timeout
per-specialist budget
global investigation budget
```

Acceptance:

```text
state isolation
no evidence cross-contamination
deterministic budget enforcement
secondary Specialist selection remains DB-driven
persisted result links remain valid
```

---

## C.10 - Remediation Proposal and Sandbox Validation

Add remediation planning only after diagnosis is grounded.

Expose high-level controlled functions:

```text
propose_remediation
create_remediation_plan
test_remediation_in_sandbox
get_sandbox_result
request_user_approval
apply_approved_remediation
```

Rules:

```text
no production write-capable action before sandbox validation
no production write-capable action before project policy authorization
ask the user whenever risk or approval rules require it
record before/after evidence
record rollback expectations when applicable
```

Acceptance:

```text
solution proposal is linked to diagnosis claims/evidence
sandbox test result is persisted and auditable
failed sandbox test blocks production application
high-risk action asks the user
policy-denied action cannot be applied
```

---

## C.11 - Orchestration Equivalence Gate

This is the point at which we decide whether orchestration ownership may move
from LangGraph/Python to Claude.

Create a regression/evaluation matrix using existing Phase 4 scenarios plus
remediation-planning cases:

```text
high CPU
high memory
CPU + memory same process
service failure
disk issue
insufficient evidence
conflicting specialists
no suitable Specialist
tool denied
budget exhausted
provider/runtime failure
Ollama timeout / invalid JSON
safe remediation proposal
sandbox remediation failure
approval-required remediation
```

Compare old and new paths for:

```text
routing correctness
specialist completion
evidence grounding
budget compliance
conflict preservation
final diagnosis grounding
policy safety
provider/runtime resilience
fixed workflow preservation
sandbox validation behavior
latency
tool calls
cost
```

Gate rule:

```text
if a safety, grounding, workflow-order, or policy metric regresses materially,
the current orchestration remains authoritative
```

---

## C.12 - Switch High-Level Orchestration Ownership

Only after C.11 passes, Claude Supervisor becomes the primary coordinator for:

```text
monitoring cycle decisions
analysis sequencing
investigation initiation
Specialist coordination
follow-up decisions
final coordination
remediation proposal and sandbox validation coordination
```

Existing services continue to perform operational functions.

Rollback:

```text
AGENT_ORCHESTRATION_MODE=current
AGENT_ORCHESTRATION_MODE=claude
```

Exact configuration naming will be chosen during implementation.

---

## C.13 - Controlled Deprecation of Duplicated Orchestration

Only after the Claude path has been stable and accepted may duplicated
orchestration be removed.

Potential candidates:

```text
duplicated high-level routing glue
duplicated agent loops
LangGraph nodes that only reproduce Claude supervision
```

Explicitly **not** candidates merely because Claude exists:

```text
MonitoringService
ReportService
RAG
Knowledge RAG
SSH layer
Tool Registry
Policy
Evidence
Investigation persistence
Specialist Registry
DB models/repositories
Admin UI/API
Scheduler
Ollama clients
```

Every deletion requires:

```text
dependency check
test replacement
documentation update
rollback consideration
```

---

# Repository Structure Target

The target addition is:

```text
chat_system/
  CLAUDE.md
  .mcp.json
  .claude/
    settings.json
    rules/
    commands/
    skills/
    agents/
    hooks/
  app/
    admin/
    agent/
    integrations/
      claude/
    mcp/
    shared/
    bootstrap.py
    main.py
  tests/
  docs/
```

Existing project structure is preserved and evolved incrementally.

---

# Testing Policy For Every Transition Step

Every implementation step must include, as applicable:

```text
unit tests
negative tests
integration tests
runtime acceptance
persistence checks
policy boundary checks
Ollama provider/structured-output checks
documentation synchronization
```

A passing happy path alone is not sufficient.

---

# Security Invariants During Transition

These are non-negotiable:

```text
1. Claude may request; Python authorizes.
2. No arbitrary shell tool for normal agent operation.
3. No raw production SSH tool exposed to Claude.
4. Registered tools and typed parameters remain enforced.
5. Specialist permissions remain persisted and validated.
6. Evidence IDs and source provenance remain validated.
7. Existing budgets cannot be replaced by prompt instructions.
8. Ollama remains the operational LLM provider for project reasoning.
9. Runtime timeout/cancellation must be enforceable outside Claude.
10. Remediation must be sandbox-tested before production application.
11. Production application must ask the user whenever policy requires approval.
12. The current safe execution path remains available until migration acceptance.
```

---

# Effect On Project Roadmap

The roadmap becomes:

```text
Phase 4   Autonomous Diagnosis                      COMPLETE
Phase C   Claude Code Supervisory Runtime Transition NEXT
Phase 5   Supervised Remediation
Phase 6   Sandbox Validation
Phase 7   Autonomous Remediation Policies
Phase 8   Telegram Operations
Phase 9   Analytics & Dashboards
Phase 10  Productization & Architecture Cleanup
```

Phase 5 does not begin until the supervisory transition reaches its accepted
target state, unless an explicit new ADR changes this ordering.

---

# First Implementation Step

The first coding step after documentation acceptance is:

```text
C.1 - Claude Code project structure
```

Create the minimal `CLAUDE.md`, `.mcp.json` placeholder/configuration, and
`.claude/` rules/agent/skill skeleton required for this project.

No existing runtime behavior changes in C.1.
