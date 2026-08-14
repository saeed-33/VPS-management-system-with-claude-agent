# Phase 4.17 Closeout — Dynamic Secondary Specialist Routing

**Status:** COMPLETED  
**Next:** Phase 4.18 — Correlation + Final Diagnosis

## Capability accepted

Phase 4.17 adds bounded dynamic follow-up Specialist waves on top of the Phase 4.16 Claude-supervised parallel coordinator.

The runtime now supports:

```text
primary Specialist wave
 -> recommendation inspection
 -> Registry validation
 -> duplicate suppression
 -> global Specialist/action budget validation
 -> secondary Specialist wave
 -> accumulated Evidence propagation
```

## Acceptance evidence

Controlled Secondary Runtime Acceptance:

```text
Report ID:                1076
Server ID:                2
Initial Specialist:       nginx
Controlled Secondary:     systemd-service
Execution mode:           dynamic-secondary
Status:                   completed
Waves completed:          2
Actions used:             3/10
Executed Specialists:     nginx, systemd-service
Secondary requested:      systemd-service
Secondary accepted:       systemd-service
```

Checks:

```text
primary_completed: PASS
controlled_recommendation_injected: PASS
two_waves_completed: PASS
secondary_requested: PASS
secondary_accepted_by_real_4_17: PASS
secondary_executed: PASS
secondary_completed: PASS
global_action_budget_safe: PASS
specialist_budget_safe: PASS
no_duplicate_specialists: PASS
```

## Automated baseline

Latest recorded regression baseline:

```text
184 passed, 1 warning
```

## Ollama reliability work

The Gemma model advertises a large maximum context length, while the Ollama runtime had initially loaded it with a much smaller context.

The accepted runtime configuration was verified at:

```text
CONTEXT = 32768
```

Final Synthesis uses a compact provider contract so the model can return complete structured JSON without spending output budget on structures that are unnecessary after Tool execution has ended.

Generation capacity remains separate from context capacity.

## Architectural conclusion

Phase 4.17 is considered complete because the orchestration path has been proven independently from the stochastic question of whether a particular model run chooses to recommend a secondary Specialist.

Natural recommendation quality remains an evaluation dimension.

## Phase 4.18 entry criteria

Phase 4.18 may now consume multiple Specialist results and accumulated Evidence to produce a server-level diagnosis.

Required semantics:

```text
confirmed
probable
unknown
```

Every material diagnosis claim must be traceable to actual Evidence and/or explicitly attributed technical Knowledge.

Conflicting Specialist conclusions must remain visible rather than being silently flattened.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
