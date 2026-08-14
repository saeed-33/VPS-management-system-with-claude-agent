# Investigation and Specialist Workflow

```text
analysis claims
  -> InvestigationRouter candidates
  -> DB-defined Specialist selection
  -> context builder with owned persisted data
  -> policy evaluation and budget checks
  -> registered read-only tool calls
  -> Specialist reasoning result
  -> EvidenceCollectionService.collect(...)
  -> persisted loop/runtime snapshot
  -> correlation and conflict preservation
  -> grounded final diagnosis
```

The loop owns the actual Evidence collection. Persistence links the returned
Evidence into the continuous investigation store; it does not recreate a
second Evidence collection system.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
