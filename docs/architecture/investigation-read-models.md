# Investigation Read Models — Phase 4.19.1

Phase 4.19 starts with an operator-facing read boundary before API or HTML work.

The existing persistence stores routing state and Specialist candidates, but it does not yet store Specialist runtime runs, Evidence, correlated claims, conflicts, Final Diagnosis, or the final narrative.

The UI must not fabricate those fields.

`InvestigationReadService` exposes stable summary/detail read models. Runtime data is considered available only when a persisted `metadata["runtime_snapshot"]` object exists.

Reserved runtime snapshot fields include:

```text
status
orchestrator
execution_mode
waves_completed
actions_used
evidence_count
specialist_runs
evidence
correlated_claims
conflicts
final_diagnosis
narrative
metadata
```

Phase 4.19.1 reads this shape but does not create it.

Next: Phase 4.19.2 Runtime Snapshot Persistence.
