# Investigation Router

**Phase:** 4.5.2  
**Status:** Implemented — pending acceptance verification

The Router now separates candidate retrieval from the execution/selection
budget.

```text
Registry
  -> deterministic candidate retrieval
  -> candidate_specialists (default <= 12)
  -> future intelligent/LLM selector
  -> selected_specialists (default <= 4)
  -> future execution
```

`candidate_specialists` is intentionally a higher-recall shortlist.
`selected_specialists` is the smaller baseline selection.

The current implementation still selects deterministically from the
candidate shortlist. A later LLM Selector can replace only this selection
step without changing persistence contracts.

Defaults:

```text
candidate_limit = 12
selection_limit = 4
```

`InvestigationBudget.max_specialists=4` remains an execution budget; it is
not the candidate retrieval limit.

The Router remains dynamic: domains, trigger hints and priority are loaded
from user-defined Specialist definitions. No Specialist type is hard-coded.

Acceptance:

```powershell
uv run python -m pytest
uv run python tools/dev/inspect_investigation_routing.py 807
uv run python tools/dev/inspect_investigation_routing.py 825
```

The inspection tool prints candidate and selected sections separately.

## Regression coverage

Phase 4.5 retains explicit regression tests for healthy routing, CPU,
Memory, combined CPU + Memory, domain-only fallback, no suitable
Specialist, connection failure, info-only findings, and the independent
candidate/selection limits.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
