# Admin UI Architecture

The Admin surface uses FastAPI routes, Jinja2 templates, vanilla JavaScript,
and the existing CSS. `base.html` defines navigation and role context;
`app.js` owns the canonical `apiRequest` helper, CSRF header injection,
structured JSON/plain error parsing, non-2xx failure handling, and permission
visibility. Page-specific scripts render server, profile, report,
investigation, remediation, autonomous, and system data.

The main functional screens are Servers, Monitoring Profiles, Investigations,
Reports, Specialists, Remediation, Autonomous Policies/Candidates/History/
Decisions/Runtime/Reservations/Authorizations, Audit, and System/Safety.
Viewer receives read-only visibility; Operator receives supervised control;
Admin receives management and autonomous policy lifecycle operations. Hiding a
button is only usability; middleware and API permission mapping remain the
authority.

The Remediation page cannot create arbitrary issue fingerprints, issue manual
authorization tokens, skip policy/sandbox/approval, or send raw SSH/SQL. It
reads persisted plans and Evidence, calls the existing API gates, and shows
structured errors without reloading after failed AJAX operations.

The System/Safety page displays `automatic_remediation_allowed`, the V1 action
allowlist/risk ceiling, sandbox attestation state, MCP count, scheduler state,
and Admin session settings. It has no autonomy toggle.

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
