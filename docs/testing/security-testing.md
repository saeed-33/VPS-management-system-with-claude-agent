# Security Testing

Security tests assert both positive controls and negative space:

- role matrix, session expiry, failed login, logout, API 401/403, and CSRF;
- forbidden raw SSH/SQL/shell and unrestricted MCP capability strings;
- policy ambiguity, missing fingerprint, unsupported action, high risk,
  missing/stale/mismatched sandbox, incomplete Evidence, and circuit suspension;
- single-use authorization replay, idempotency collision, lease recovery,
  competing worker ownership, and stale finalization;
- Admin UI absence of force/skip/manual-token controls and safe serialization
  of reservations/authorizations.

The complete negative/security suite is part of the 586-test current run.

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
