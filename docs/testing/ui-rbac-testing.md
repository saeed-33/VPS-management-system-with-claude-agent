# Admin UI and RBAC Testing

`tests/test_admin_auth_rbac.py` verifies authentication, session, RBAC, CSRF,
and API/Web response differences. `tests/test_admin_ui_completion.py` verifies
all current Admin pages, navigation, compatibility redirect, safe target
labels, reservation token omission, remediation safety controls, and role
markers. System and Phase 5 Admin tests cover runtime safety payloads and
remediation route presence.

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
