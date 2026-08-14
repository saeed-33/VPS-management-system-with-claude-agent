# Sandbox Validation Workflow

```text
persisted plan + target server
  -> persisted safety designation check
  -> native Sandbox/WSL2 attestation check
  -> exact plan/action/target binding
  -> execute registered validation action
  -> collect Before Evidence
  -> validate action in isolation
  -> collect After Evidence
  -> verify restoration and fingerprint
  -> persist passed/failed/stale result and audit
```

The server safety designation is based on persisted metadata markers; a
hostname alone never makes a target safe. Missing native runtime or attestation
fails closed.

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
