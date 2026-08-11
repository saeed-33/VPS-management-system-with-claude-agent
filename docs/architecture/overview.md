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

Reference automated regression baseline immediately before documentation closeout:

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
LangGraph Investigation Coordinator
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

## Routing

`InvestigationRouter` is deterministic and conservative.

It decides:

```text
should_investigate
detected_domains
candidate_specialists
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

## LangGraph orchestration

LangGraph owns orchestration, not domain authority.

It coordinates:

```text
parallel Specialist execution
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

Phase 5 must introduce a separate Remediation Plan, approval model, risk classification, audit trail, before/after Evidence, and rollback semantics before any write-capable action is allowed.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
