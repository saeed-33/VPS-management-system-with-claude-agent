# Incident Lifecycle

```text
observe -> report -> analyze -> investigate when needed -> diagnose
  -> propose -> sandbox -> approve or deny
  -> execute -> verify -> rollback if needed -> audit -> close
```

Autonomous remediation is a separate optional branch behind the global
fail-closed switch. A closed incident keeps structured fingerprints, Evidence,
decision outcomes, and audit links for future candidate/history evaluation.

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
