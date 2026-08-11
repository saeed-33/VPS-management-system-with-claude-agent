# Current Workflows

<!-- DOC-STATUS: CURRENT -->

## Monitoring and analysis

```text
Load Server
 -> validate monitoring configuration
 -> SSH monitoring commands
 -> build/save Monitoring Report
 -> enqueue analysis
 -> normalize/fingerprint
 -> reuse policy / Incident RAG
 -> LLM when required
 -> save/index Analysis
```

## Claude-supervised workflow

Phase C preserves this fixed workflow:

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

Claude Code owns high-level coordination. The project services remain
authoritative for monitoring, RAG retrieval,
Ollama-backed LLM calls, Specialist definitions, evidence, policy, persistence,
sandbox validation, and user approval gates.

## Investigation routing and persistence

```text
Monitoring Report
+ Initial Analysis
+ SpecialistRegistrySnapshot
 -> InvestigationRouter
 -> should investigate?
 -> detected domains
 -> selected Specialists
 -> persist routing decision
```

Healthy/no-issue analysis does not start an unnecessary Investigation.

## Specialist execution

```text
SpecialistTask
+ Specialist instructions
+ Initial Analysis
+ current Evidence
+ Incident RAG
+ Knowledge RAG
 -> SpecialistContextBuilder
 -> SpecialistReasoningAgent
 -> optional Diagnostic Tool request
 -> DiagnosticPolicyEngine
 -> ALLOW / DENY
 -> EvidenceCollectionService
 -> known read-only SSH command
 -> Evidence
 -> rebuild context
 -> repeat within budgets
 -> Final Synthesis
```

Unknown Evidence/Knowledge IDs are rejected.

## Claude-Supervised Orchestration

```text
selected Specialists
 -> Claude-supervised Specialist coordination
 -> bounded Specialist loops
 -> deterministic aggregation
 -> recommended_next_specialists
 -> validate against Registry/budgets
 -> optional secondary wave
```

## Correlation and Final Diagnosis

```text
SpecialistResults
+ Evidence
 -> CrossSpecialistCorrelator
 -> correlated claims
 -> explicit conflicts
 -> confirmed/probable/unknown
 -> FinalDiagnosis
 -> FinalDiagnosisSynthesizer
```

Narrative generation cannot introduce unknown Claim/Conflict IDs.

## Persistence and read workflow

```text
Runtime result
+ Evidence
+ correlated claims/conflicts
+ Final Diagnosis
+ narrative
 -> InvestigationRuntimeSnapshotService
 -> database metadata/runtime snapshot
 -> InvestigationReadService
 -> REST API
 -> read-only Administration UI
```

## Evaluation workflow

```text
deterministic evaluation dataset
+
controlled routing/provider/policy failure injection
+
persisted real runtime snapshots
 -> EvaluationObservation[]
 -> ProductionReadinessGate
```

Current accepted state:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Random Linux workload workflow

```text
seeded safe workload on disposable Linux VM
 -> monitoring report
 -> analysis
 -> Investigation
 -> Specialist diagnosis
 -> persisted Evidence/Diagnosis
 -> persisted runtime evaluation
 -> aggregate readiness
```

See `../testing/RUNTIME_SCENARIOS.md`.

## Phase 5 boundary

Phase 5 remediation workflow must remain policy-gated:

```text
diagnosis
 -> proposed RemediationPlan
 -> isolated-environment test
 -> risk classification
 -> human/operator approval
 -> bounded write-capable action
 -> before/after Evidence
 -> validation
 -> rollback when required
```

That workflow is not implemented yet.

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
