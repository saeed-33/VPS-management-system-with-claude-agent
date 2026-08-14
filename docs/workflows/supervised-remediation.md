# Supervised Remediation Workflow

```text
grounded diagnosis
  -> immutable plan + plan fingerprint
  -> registered native sandbox validation
  -> persisted approval request bound to exact fingerprint
  -> human approve/reject
  -> registered named write outside unrelated UI logic
  -> Before/After Evidence and verification
  -> success or registered rollback
  -> remediation audit
```

The UI can request each gate but cannot bypass it. High/critical actions are
not auto-approved. Rejection, expired approval, CSRF failure, wrong actor,
fingerprint mismatch, or sandbox failure stops the path.

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
