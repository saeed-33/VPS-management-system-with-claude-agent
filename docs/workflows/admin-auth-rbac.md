# Admin Authentication and RBAC Workflow

```text
login credentials
  -> scrypt verification
  -> server-side session + digest persistence
  -> request middleware authenticates cookie
  -> permission mapper checks role
  -> mutating request requires CSRF token
  -> operation executes through API/service
  -> Admin auth/operation audit event
```

Viewer is read-only, Operator controls monitoring and supervised remediation,
and Admin manages resources and autonomous policy lifecycle. Unauthenticated
API calls return 401; insufficient permission or CSRF returns 403; Web users
are redirected to login.

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
