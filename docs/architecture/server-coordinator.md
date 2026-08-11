# Server Coordinator — Phase 4.15

**Status:** Implemented and runtime accepted

Phase 4.15 introduced the server-level composition boundary:

```text
Routing Decision
 -> Server Coordinator
 -> selected dynamic Specialists
 -> Specialist Investigation Loop
 -> shared Investigation budgets
 -> SpecialistResults + Evidence
 -> ServerInvestigationState
```

The Coordinator composes existing Registry, Specialist Loop, Policy, Evidence, RAG, and SSH boundaries rather than duplicating them.

Specialists remain operator-defined Registry data.

Partial Specialist failure is isolated so successful sibling results remain available.

## Evolution after 4.15

Phase 4.15 established the sequential Coordinator baseline.

Phase 4.16 retained the same domain responsibilities but replaced sequential independent Specialist execution with bounded Claude-supervised parallel fan-out/fan-in.

Phase 4.17 added an outer dynamic-secondary routing loop:

```text
initial Specialist wave
 -> aggregate results/evidence
 -> inspect recommended_next_specialists
 -> Registry validation
 -> duplicate suppression
 -> remaining budget validation
 -> optional next Specialist wave
```

Thus the Claude-supervised runtime uses the Server Coordinator concept as a hierarchical investigation boundary while Claude manages stateful parallel/dynamic orchestration.

## Global budget invariants

```text
executed Specialists <= InvestigationBudget.max_specialists
actual actions <= InvestigationBudget.max_actions
no Specialist slug executes twice
```

Parallel workers receive deterministic quotas whose sum does not exceed the available global action budget.

Later waves receive only remaining budget.

## Current boundary

Cross-Specialist correlation and final server-level diagnosis remain **Phase 4.18**.

Phase 4.18 must consume multiple Specialist results and accumulated Evidence without weakening existing provenance or safety boundaries.

Remediation remains outside Phase 4.

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
