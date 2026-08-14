# Admin Authentication and RBAC

Admin authentication is a local, database-backed boundary for the FastAPI
Admin Web UI and Admin API. It is independent from Claude and MCP.

## First administrator

Apply the additive migration, then create the first account interactively:

```bash
uv run --no-sync python -m tools.create_admin --username admin
```

The command prompts twice for the password and never prints it or creates a
default account. The username must be 3–120 characters and the password must
contain at least 12 characters. Use `--role viewer`, `--role operator`, or
`--role admin` when creating a non-admin account.

## Runtime settings

Configure `ADMIN_SESSION_SECRET` externally as a stable random secret of at
least 32 characters. Production startup rejects an empty or weak secret and
requires `ADMIN_SESSION_SECURE=true`. Only explicit `DEBUG=true` local
development may use the process-local fallback, which invalidates all
sessions on process restart. `ADMIN_SESSION_TTL_SECONDS` controls expiry,
`ADMIN_SESSION_COOKIE_NAME` controls the cookie name, and
`ADMIN_SESSION_SECURE=true` enables the Secure cookie flag for HTTPS.

## Roles and permissions

- `viewer`: read-only Admin access, including servers, profiles, commands,
  specialists, knowledge, monitoring, investigations, reports, remediation,
  autonomous history, audit, and system status.
- `operator`: viewer permissions plus `monitoring.control`,
  `remediation.approve`, `remediation.execute`, and
  `remediation.rollback`.
- `admin`: viewer permissions plus server/profile/command/specialist/knowledge
  administration, all autonomous policy lifecycle permissions, and
  `system.admin`.

The mapping is centralized in `app/interfaces/admin/auth.py`. Backend checks
remain authoritative even when the UI hides controls.

## Sessions, CSRF, and routes

`POST /login` creates an opaque server-side session. Only a SHA-256 digest is
stored in `admin_sessions`; passwords are stored as scrypt verifiers in
`admin_users`. The HttpOnly, SameSite=Lax cookie is never exposed to
JavaScript, expires according to the configured TTL, and is revoked by
`POST /logout`.

Browser writes use the HMAC-derived CSRF token rendered in the base template
and sent by `app.js` as `X-CSRF-Token`. Unauthenticated Web requests redirect
to `/login`; unauthenticated API requests return 401 and forbidden requests
return 403.

Authentication and privileged operation events are stored in
`admin_auth_audit_events`, without password contents. The migration is
`app/infrastructure/database/migrations/step_8_1_admin_auth.sql` and is
additive; it preserves all existing Phase 7 tables and data.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **OPERATIONS**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: real acceptance PASS; Specialist final E2E partial and accepted
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
