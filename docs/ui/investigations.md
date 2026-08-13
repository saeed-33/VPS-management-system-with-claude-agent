# Investigation Administration UI

<!-- DOC-STATUS: CURRENT -->

The Investigation UI is read-only.

## Pages

```text
/investigations
/investigations/{investigation_id}
```

The pages expose persisted Investigation state through the same read model used by the API.

Expected detail information includes, when available:

```text
Investigation identity/status
server/report/analysis identity
routing/budgets
Specialist runs
Evidence
correlated claims
conflicts
Final Diagnosis
narrative
runtime/final-diagnosis availability
```

The UI must preserve Evidence/Claim/Conflict provenance and must not provide remediation controls during Phase 4.

Current operational state:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

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
