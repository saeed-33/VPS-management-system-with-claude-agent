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

## LangGraph orchestration

```text
selected Specialists
 -> parallel LangGraph wave
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

The next workflow must be supervised remediation:

```text
diagnosis
 -> proposed RemediationPlan
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

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
