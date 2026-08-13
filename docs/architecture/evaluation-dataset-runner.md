# Evaluation Dataset & Deterministic Runner — Phase 4.20.2

Phase 4.20.2 introduces the repeatable evaluation dataset and runner.

## Purpose

This step does **not** claim measured runtime quality.

It verifies that:

- every readiness metric has enough evaluation cases;
- case IDs are stable and unique;
- observations are generated consistently;
- the Phase 4.20.1 readiness gate receives the correct metrics;
- hard safety failures block readiness.

## Dataset coverage

The default dataset contains deterministic fixtures for:

```text
routing
specialist completion
evidence grounding
budget compliance
conflict preservation
final diagnosis grounding
provider resilience
policy safety
```

The dataset contains enough samples to satisfy every default minimum sample threshold from Phase 4.20.1.

## Important distinction

`expected_behavior_executor` is a dataset-validation executor only.

It proves:

```text
dataset -> observations -> readiness gate
```

It does not prove:

```text
real runtime -> correct outcome
```

Runtime-backed measurement begins in Phase 4.20.3.

## Phase 4.20.3

The next step adds executors that use real or controlled-runtime components to measure actual system behavior and emit observations into the same runner.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
