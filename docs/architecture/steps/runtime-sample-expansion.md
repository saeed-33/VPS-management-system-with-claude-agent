# Runtime Sample Expansion — Phase 4.20.6

Phase 4.20.6 collects additional real persisted Investigation runtime samples required by the Production Readiness Gate.

## Why this exists

Phase 4.20.5 currently has full coverage for:

```text
routing_recall
provider_resilience
policy_safety
```

but only one persisted runtime sample for:

```text
specialist_completion
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
```

The gate requires 10 runtime samples for most of these metrics and 5 conflict-preservation samples.

## Real execution

Every new sample executes:

```text
real Claude-supervised parallel coordinator
real Specialist loops
real Ollama reasoning
real Policy
real SSH diagnostic tools
real Evidence collection
real correlation
real narrative synthesis
real runtime snapshot persistence
```

The initial Specialist pair is controlled for evaluation repeatability.

Conflict fixtures are controlled findings backed by real runtime Evidence. They are used only until the configured conflict-sample target is reached.

## Database effect

Each successful sample creates and retains a new Investigation record and persisted runtime snapshot.

No schema migration occurs.

## Default target

The tool inspects existing persisted snapshots and only creates the deficit required to reach:

```text
runtime snapshots: 10
conflict snapshots: 5
```

Use `--max-new` to limit how many real runs occur in one invocation.

## After expansion

Run:

```text
uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500
```

The aggregate gate will then decide whether Phase 4.20 can close as `ready_for_supervised_operations`.

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
