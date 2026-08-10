# Current Workflows

## Monitoring and initial analysis

```text
Load server
 -> validate monitoring configuration
 -> SSH monitoring commands
 -> build/save report
 -> enqueue analysis
 -> normalize + fingerprint
 -> Incident Hybrid Retrieval
 -> LLM when required
 -> save/index analysis
```

Exact fingerprint reuse and semantic retrieval remain distinct mechanisms.

## Investigation routing

```text
Monitoring Report
+ Initial Analysis
+ SpecialistRegistrySnapshot
 -> actionable signal?
 -> detect domains
 -> rank enabled Specialists
 -> InvestigationRoutingDecision
```

Healthy reports do not open investigations merely because Specialists exist.

## Specialist context

```text
SpecialistTask
+ Specialist Instructions
+ Initial Analysis
+ current Evidence
+ Incident RAG
+ Knowledge RAG
 -> SpecialistContextBuilder
 -> bounded provenance-bearing context
```

## Single-Specialist investigation

```text
reason
 -> optional registered Tool requests
 -> Diagnostic Policy
 -> ALLOW/DENY
 -> Evidence Collection over bounded SSH
 -> rebuild context
 -> reason again
 -> final synthesis
```

Only actual approved SSH executions consume action budget.

Duplicate Tool requests do not consume another action.

## Multi-Specialist orchestration

```text
Investigation Router
 -> selected Specialists
 -> LangGraph parallel wave
 -> SpecialistInvestigationLoop per worker
 -> deterministic aggregation
```

Parallel workers receive deterministic action quotas whose sum never exceeds the global Investigation budget.

## Dynamic secondary routing

```text
wave 1 results
 -> collect recommended_next_specialists
 -> validate against enabled Registry
 -> remove already executed Specialists
 -> enforce remaining specialist/action budget
 -> optional next parallel wave
 -> repeat while bounded
```

Recommendations are advisory. The model cannot create an executable Specialist.

Later waves receive accumulated Evidence from previous waves.

## Final synthesis

Normal reasoning uses the rich Specialist reasoning contract.

When the loop enters Final Synthesis mode, the Ollama provider uses a compact structured result:

```text
summary
confidence
missing_evidence
recommended_next_specialists
```

This keeps the final JSON bounded while preserving secondary-routing information.

## Accepted runtime configuration

Reference local Ollama runtime:

```text
model: gemma4:e4b-it-q4_K_M
context: 32768
```

The model advertises a larger maximum context, but runtime context is explicitly configured rather than relying on Ollama's smaller default.

## Current boundary

Phase 4.17 is accepted.

The next workflow is Phase 4.18:

```text
Specialist Results
+ Evidence
+ provenance
 -> cross-Specialist correlation
 -> confirmed/probable/unknown claims
 -> server-level Final Diagnosis
```

Phase 4 remains read-only. Autonomous remediation is still out of scope.
