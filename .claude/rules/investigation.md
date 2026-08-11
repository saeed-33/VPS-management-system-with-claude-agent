# Investigation Rule

Investigation remains project-owned state and persistence.

Claude Code may coordinate when an investigation should proceed and which
project functions to invoke, but must preserve:

```text
InvestigationRouter
Investigation persistence
SpecialistRegistry
EvidenceCollectionService
CrossSpecialistCorrelator
FinalDiagnosis contracts
runtime snapshots
```

The investigation path must follow the fixed workflow:

```text
analysis with potential issues
 -> select DB-defined Specialists
 -> run Specialist tasks through project tools
 -> collect structured Specialist results
 -> aggregate results at the per-server subordinate agent
 -> produce final diagnosis through project services
```

Do not fabricate Evidence IDs, Knowledge IDs, Claim IDs, Conflict IDs, or
persisted investigation state.
