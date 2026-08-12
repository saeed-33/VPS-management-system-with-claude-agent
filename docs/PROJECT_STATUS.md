# Project Status

<!-- DOC-STATUS: CURRENT -->

Last accepted diagnosis milestone: **Phase 4.20 complete**.

Current transition milestone: **C.14 - Real Claude-Native Orchestration**.

## Operational status

```text
diagnosis_readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
claude_native_runtime: transition_in_progress
phase_5: blocked_pending_c14
```

The Phase 4 readiness result remains valid for the accepted diagnosis
capabilities. It must not be interpreted as evidence that the new Claude-native
execution path has already passed equivalent runtime acceptance.

## Accepted Phase 4 readiness evidence

```text
runtime snapshots: 10
persisted runtime observations: 50
controlled safety observations: 30
aggregate observations: 80
readiness metrics passed: 8/8
```

Accepted metrics:

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

These metrics must be re-run against the final C.14 runtime before Phase C can
close.

## Current product capabilities

Implemented and retained:

```text
monitoring
analysis
Incident RAG
Knowledge RAG
dynamic DB-defined Specialists
diagnostic routing
read-only diagnostic tools
Policy
Evidence
cross-Specialist correlation
Final Diagnosis
runtime persistence
Investigation API/UI
evaluation and safety gate
project MCP tool surface
Claude Code project configuration
```

Not implemented/authorized for production:

```text
automatic remediation
general write-capable remediation tools
production remediation executor
real isolated remediation environment
complete approval/verification/rollback workflow
```

## Claude runtime truth

ADR-017 defines Claude Code as the intended supervisory orchestration runtime.

ADR-018 clarifies that a real Claude-native runtime means:

```text
Claude Code
  = reasoning + high-level sequencing

skills
  = operational workflow contracts

agents
  = bounded intelligent worker contracts

MCP
  = Claude's project capability interface

Python
  = execution + validation + policy + persistence + safety
```

The repository already exposes the `vps` project MCP server and Claude
configuration.

However, the scheduled production path still includes Python-owned workflow
sequencing through the current Claude-named monitoring/Specialist wrappers.
Therefore the project must not report C.14 or Phase C as complete yet.

## Completed runtime refactor milestones

```text
R.1 Runtime Package Boundary: complete
R.2 Tool Package Boundary: complete
R.3 Domain Services Boundary: complete
R.4 Admin Surface Alignment: complete
R.5 Documentation and Tests: complete
```

These remain accepted structural milestones. They do not imply that C.14's
real Claude-native execution path is complete.

## C.14 progress

```text
C.14.0 Architecture decision: COMPLETE after foundation change
C.14.1 Remove cosmetic/duplicated Claude surfaces: COMPLETE after foundation change
C.14.2 Operational Skills: COMPLETE
C.14.3 Bounded Agents: COMPLETE
C.14.4 Least privilege and model inheritance: NEXT
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

Detailed plan:

`docs/roadmap/c14-claude-native-execution-plan.md`

## `.claude` transition state

After C.14.1 the project-owned Claude surface intentionally contains:

```text
agents/
  existing transitional agents until C.14.3

skills/
  existing transitional skills until C.14.2

rules/
  safety.md
  evidence-grounding.md

settings.json
```

`.claude/commands/` is removed because it duplicated skills.

Placeholder hook documentation is removed. Hooks will only be introduced in
C.14.5 when they enforce or audit a concrete runtime condition.

## LLM provider

Ollama remains the configured LLM provider.

C.14.7 must prove the actual Claude runtime launch path through the supported
Ollama integration. Agent model configuration must inherit the session runtime
model instead of hard-coding an Anthropic model alias.

## Phase 5 gate

Phase 5 - Supervised Remediation follows only after C.14.14.

Before Phase 5:

```text
real Claude session launch must work
Claude must see and use project MCP tools
operational skills must be executable contracts
bounded agents must be used by the runtime
high-level sequencing must move out of duplicate Python orchestration
runtime observability must be sufficient
safety/readiness evaluation must pass again
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
diagnosis_readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
Claude-native runtime transition: C.14 in progress
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
