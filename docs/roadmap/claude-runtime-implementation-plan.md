# Claude Runtime Implementation Plan

## Operating Principle

Claude is the intended supervisory runtime. The application exposes durable
tools, records, policies, and administrative controls.

The accepted C.14 clarification is:

```text
Claude decides WHAT/NEXT.
Python decides WHETHER ALLOWED and HOW TO EXECUTE SAFELY.
```

Before adding Python high-level workflow control, verify whether Claude can make
the decision through structured project tools. If yes, keep that decision in
Claude.

Python remains responsible for:

```text
database persistence
SSH execution through registered commands
MCP/project tool implementations
RAG retrieval
project-owned Ollama client calls
policy checks
evidence validation
sandbox/remediation authorization
admin API and UI
audit logs
```

## Fixed Workflow

```text
periodic monitoring
 -> per-server Claude session
 -> monitoring completion
 -> exact historical report lookup
 -> exact match: reuse stored analysis
 -> otherwise retrieve top similar historical reports
 -> Ollama-backed analysis
 -> issue detection
 -> DB-defined Specialist selection
 -> bounded specialist investigation
 -> evidence-grounded aggregation
 -> final diagnosis
 -> remediation proposal when needed
 -> isolated validation when implemented
 -> production action only through accepted policy/approval contracts
```

## R.5 - Documentation and Tests

Status: **COMPLETE**

R.5 remains an accepted completed refactor milestone. It established the
documentation/test contract for the Claude runtime transition, including
runtime documentation, project structure documentation, the generated test
catalog, and documentation regression tests.

Its completion remains valid while C.14 changes the runtime implementation.
C.14 must update those documents rather than erasing the accepted R.5 milestone.

## Completed structural refactors

```text
R.1 Runtime Package Boundary: COMPLETE
R.2 Tool Package Boundary: COMPLETE
R.3 Domain Services Boundary: COMPLETE
R.4 Admin Surface Alignment: COMPLETE
R.5 Documentation and Tests: COMPLETE
```

These refactors preserve the project-owned capability boundary. They do not by
themselves prove that a live Claude session owns production orchestration.

## C.14 - Real Claude-Native Orchestration

Status: **IN PROGRESS**

Detailed plan:

`docs/roadmap/c14-claude-native-execution-plan.md`

### Accepted truth

Already implemented:

```text
project-scoped vps MCP registration
stdio MCP protocol server
project tool schemas/dispatch
Claude Code permission settings
transitional agent frontmatter
runtime/job persistence primitives
Python supervisor/scheduler integration
```

Not yet accepted as Claude-native:

```text
production monitoring sequencing
production Specialist sequencing
real Ollama-backed Claude session launch
operational skill execution
final bounded agent design
runtime hook enforcement/audit
Claude session observability
end-to-end Claude/Ollama/MCP acceptance
```

### C.14 work status

```text
C.14.0 Architecture decision: COMPLETE after foundation change
C.14.1 Remove cosmetic/duplicated Claude surfaces: COMPLETE after foundation change
C.14.2 Operational Skills: NEXT
C.14.3 Bounded Agents: PENDING
C.14.4 Least privilege and model inheritance: PENDING
C.14.5 Concrete Hooks: PENDING
C.14.6 ClaudeSessionRunner: PENDING
C.14.7 Ollama-backed Claude runtime: PENDING
C.14.8 MCP boundary refactor: PENDING
C.14.9 Remove duplicate Python orchestration: PENDING
C.14.10 Session/job observability: PENDING
C.14.11 Runtime acceptance tests: PENDING
C.14.12 Readiness and safety reevaluation: PENDING
C.14.13 Documentation synchronization: PENDING
C.14.14 Phase C closure: PENDING
```

## Target Runtime Shape

```text
Scheduler
 -> ClaudeSupervisor
 -> real Claude session via configured Ollama launch path
 -> server supervisor / operational skills
 -> Project MCP tools
 -> Python domain services / policy / evidence
 -> Repositories / SSH / RAG / Ollama
```

Claude owns allowed workflow decisions. The project owns capability execution
and authorization.

## Phase 5 gate

Phase 5 - Supervised Remediation does not begin until C.14.14 is accepted.

The existing remediation scaffolding remains non-authoritative for production
write execution and `automatic_remediation_allowed` remains false.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
Claude-native runtime transition: C.14 in progress
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
