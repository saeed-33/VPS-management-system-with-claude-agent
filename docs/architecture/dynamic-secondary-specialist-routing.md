# Dynamic Secondary Specialist Routing — Phase 4.17

Phase 4.17 adds bounded, conditional follow-up Specialist routing above the
accepted 4.16 parallel LangGraph coordinator.

```text
initial routing
    |
    v
parallel wave 1
    |
    v
inspect recommended_next_specialists
    |
    +-- none / no budget / no slots --> finalize
    |
    v
validate against enabled Registry
    |
    v
parallel wave 2
    |
    v
inspect recommendations again
    |
    +-- bounded loop --> ...
```

## Design constraints

Recommendations are advisory. A model cannot create a Specialist.

A recommendation is accepted only when:

1. its slug exists in the enabled Specialist Registry snapshot;
2. it has not already executed in the Investigation;
3. an Investigation Specialist slot remains;
4. action budget remains.

The graph may execute more than one follow-up wave, but the loop is bounded by
`InvestigationBudget.max_specialists` and `InvestigationBudget.max_actions`.

## Budget behavior

Wave 1 receives the original budget.

After a wave finishes, actual action usage is subtracted from the global
budget. The next wave receives only the remaining action budget.

This is safe because waves are sequential relative to one another even though
Specialists inside each wave can execute in parallel using Phase 4.16.

## Evidence behavior

Every later wave receives the accumulated Evidence from all previous waves.
Evidence remains deduplicated by `evidence_id`.

## Why a graph above the 4.16 graph

Phase 4.16 already has accepted parallel fan-out/fan-in behavior. 4.17 composes
that stable graph instead of rewriting its worker execution path.

This gives two clear orchestration levels:

```text
outer graph: dynamic follow-up waves
inner graph: bounded parallel Specialists within one wave
```

## Out of scope

Cross-Specialist correlation and final diagnosis remain Phase 4.18.
