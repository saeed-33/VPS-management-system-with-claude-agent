# Dynamic Secondary Specialist Routing — Phase 4.17

**Status:** Implemented and runtime accepted.

Phase 4.17 adds bounded, conditional follow-up Specialist routing above the accepted Phase 4.16 Claude-supervised parallel coordinator.

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

## Decision boundary

`recommended_next_specialists` is advisory model output. It is never an execution command.

A recommendation is accepted only when:

1. its slug exists in the enabled Specialist Registry snapshot;
2. it has not already executed in the Investigation;
3. an Investigation Specialist slot remains;
4. global action budget remains.

The model cannot fabricate an executable Specialist identity.

## Claude-supervised composition

Phase 4.17 deliberately composes the accepted 4.16 graph rather than replacing it.

```text
outer graph: dynamic follow-up waves
inner graph: bounded parallel Specialists within one wave
```

Specialists inside one wave may run concurrently. Waves themselves are sequential because a later wave depends on recommendations and Evidence produced by an earlier wave.

## Budget semantics

Wave 1 receives the available Investigation budget.

After each wave, actual action usage is deducted from the global action budget. A later wave receives only the remaining budget.

Invariants:

```text
total actual actions <= InvestigationBudget.max_actions
executed specialists <= InvestigationBudget.max_specialists
no Specialist slug executes twice
```

Phase 4.16 per-worker quota safety remains in force inside each parallel wave.

## Evidence propagation

Later waves receive accumulated Evidence from previous waves.

Evidence remains provenance-bearing and deduplicated by `evidence_id`. Specialist reasoning may cite only IDs actually present in its bounded context.

## Final synthesis behavior

A Specialist Investigation Loop may enter synthesis-only mode when no useful additional Tool execution is possible or when the final reasoning pass is required.

For Ollama, the runtime uses a deliberately small Final Synthesis output contract to reduce structured-output truncation risk:

```text
summary
confidence
missing_evidence
recommended_next_specialists
```

Normal reasoning retains the richer contract containing findings, hypotheses, ruled-out conclusions, provenance references, missing evidence, recommendations, and diagnostic Tool requests.

This provider-level compact synthesis contract does not weaken Evidence provenance validation during normal investigation rounds.

## Ollama context window

The deployed Gemma model advertises a much larger model context capacity, but Ollama runtime context must be configured explicitly.

The accepted local runtime was verified with:

```text
CONTEXT = 32768
```

Generation limits remain separate from context capacity. Increasing context is not treated as a reason to reduce the Final Synthesis generation budget.

## Runtime acceptance

Controlled Secondary Runtime Acceptance proved the complete two-wave execution path:

```text
Initial Specialist:       nginx
Controlled Secondary:     systemd-service
Execution mode:           dynamic-secondary
Waves completed:          2
Actions used:             3/10
Executed Specialists:     nginx, systemd-service
Secondary requested:      systemd-service
Secondary accepted:       systemd-service
```

Acceptance checks passed:

```text
primary_completed
controlled_recommendation_injected
two_waves_completed
secondary_requested
secondary_accepted_by_real_4_17
secondary_executed
secondary_completed
global_action_budget_safe
specialist_budget_safe
no_duplicate_specialists
```

Only the recommendation value was controlled in that acceptance tool. Both Specialist executions and all Registry/budget validation after the recommendation used the real runtime.

## Important limitation

Controlled acceptance proves that the orchestration correctly validates and executes a secondary recommendation.

It does not by itself prove that the LLM will always decide to recommend a secondary Specialist in every scenario where a human expects one. Recommendation quality is an evaluation concern and must be measured separately from orchestration correctness.

## Next boundary

Phase 4.18 owns cross-Specialist correlation and final server-level diagnosis.

It must distinguish confirmed, probable, and unknown conclusions and preserve an Evidence chain for every material claim.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
