# 03 - Admin UI Manual Acceptance

## 1. Disposition

**ADMIN_UI_MANUAL_ACCEPTANCE = PASS**

The initial real browser walkthrough reached the Admin UI, authenticated all
three roles, exercised a safe Admin configuration write and cleanup, and
verified viewer denial. It initially recorded PARTIAL because the visible
Logout control failed CSRF validation and the Remediation page surfaced an
existing API serialization failure. Both defects were reproduced, fixed, and
revalidated below; the final Admin UI disposition is PASS.

Only the two requested production defects were fixed. No architecture or
Admin UI redesign was introduced. No commit or push occurred. Specialist
acceptance and Phase 7 acceptance were not rerun.

## 2. Environment and startup

- Date: 2026-08-14.
- Repository: `E:\AI_VPS_Mamgment\chat_system`.
- Application: current `app.main:app` FastAPI entrypoint with Jinja2 templates,
  vanilla JavaScript, and CSS static assets.
- Browser URL: `http://127.0.0.1:8000` (the same app was also reached through
  `http://localhost:8000` to isolate browser role sessions).
- Successful startup command used:

  ```bash
  wsl.exe bash -lc 'cd /mnt/e/AI_VPS_Mamgment/chat_system && export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system" POSTGRES_HOST=172.18.128.1 && uv run --no-sync python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
  ```

- The documented host `127.0.0.1` initially failed because PostgreSQL was not
  reachable from WSL at that address. The host-only environment override above
  allowed the unchanged application to start and connect to PostgreSQL.
- `ADMIN_APP_STARTUP = PASS` after the environment correction. Startup logged
  schema initialization, scheduler startup, and Uvicorn readiness.

## 3. Accounts

The existing `tools/create_admin.py` account tool was used with interactive
password entry. Passwords and hashes are intentionally not recorded.

| Role | Acceptance username |
|---|---|
| viewer | `browser_viewer_20260814` |
| operator | `browser_operator_20260814` |
| admin | `browser_admin_20260814` |

## 4. Browser walkthrough results

### Authentication, sessions, and navigation

- `LOGIN_UI = PASS`: `/login` rendered the Username, Password, and Login
  controls; each role authenticated and reached `/`.
- `SESSION_UI = PASS`: authenticated navigation loaded protected web pages and
  unauthenticated login presentation was reachable.
- Initial `LOGOUT_UI = FAIL`: clicking the visible `Logout` form posted `/logout` and
  returned `403 CSRF validation failed` rather than navigating to `/login`.
  The form contains a hidden `csrf_token` field, while the middleware accepts
  only the `X-CSRF-Token` header or `csrf_token` query parameter. This is a
  manual UI defect, not an acceptance assumption. The corrected run posted
  the same form successfully for viewer, operator, and admin, returned
  `303 /login`, and protected navigation after logout redirected to login.
- The role sessions were isolated with separate local host cookies during the
  walkthrough; no credentials or session values are evidence.
- Navigation and presentation were usable across the Arabic and English
  labels, sidebar, dashboard cards, tables, status badges, refresh controls,
  and responsive form layouts.

### Viewer

- `VIEWER_READ = PASS`: the viewer opened the dashboard, servers, commands,
  investigations, reports, system, monitoring profiles, specialists,
  knowledge sources, Agent Runs, remediation, autonomous runtime/policies,
  candidates, history, decisions, reservations, authorizations, and audit
  screens.
- `VIEWER_FORBIDDEN_WRITE = PASS`: a harmless temporary server form submission
  was rejected by the API with `403` and the UI displayed the permission error;
  no server was created.
- The viewer saw operational forms in some pages, but the server-side
  permission boundary rejected the write. No privileged viewer write persisted.

### Operator

- `OPERATOR_LOGIN = PASS` and `OPERATOR_READ = PASS`: the operator opened the
  same operational and observability screens.
- The initial Remediation page exposed the supervised remediation lifecycle
  and its approval/sandbox language, but its data request failed with the
  serialization error recorded below. The corrected run rendered the
  persisted-plan empty state without an API error.
- Operator access to administrative configuration controls was not used to
  change persistent configuration. Focused RBAC tests separately verify that
  operator permissions do not include Admin configuration permissions.

### Admin

- `ADMIN_LOGIN = PASS`: the admin reached the dashboard and all listed pages.
- `ADMIN_CONFIGURATION_WRITE = PASS`: in Monitoring Profiles, the admin
  created `browser_acceptance_profile_20260814` with a temporary description,
  observed the success toast and list entry, then deleted it through the UI and
  confirmed it disappeared after refresh. No server, command, specialist,
  knowledge source, policy, or remediation target was changed.
- No production or arbitrary shell command was executed. Visible destructive
  and autonomous controls remained bounded by the existing server-side
  permissions, CSRF handling, sandbox/approval language, and policy runtime
  gates.

### Autonomous, remediation, safe-target, and system safety

- Autonomous Runtime, Policies, Candidates, History, Decisions, Reservations,
  Authorizations, Audit, and System pages rendered and populated from their
  API routes.
- System / Safety displayed the project tool catalog, CSRF state, session
  security fields, sandbox/safe-target/dry-run wording, and health/status
  information.
- The safe `phase5-lab` target was visible in the server and remediation
  context. No unsafe target or production execution was initiated.
- `NO_UNSAFE_EXECUTION = PASS`: no raw arbitrary command editor or ungated
  production execution was used in this acceptance.

## 5. Failures and limitations

1. The first startup attempt with PostgreSQL host `127.0.0.1` failed with
   connection refused. The unchanged application started successfully with
   `POSTGRES_HOST=172.18.128.1`.
2. The visible Logout control returned `403 CSRF validation failed`.
3. `/api/remediation` returned a server error that the UI displayed as
   `Unable to load data`; the response contained a recursive FastAPI JSON
   encoding traceback ending in `RecursionError: maximum recursion depth
   exceeded`. This affected the Remediation page for viewer, operator, and
   admin sessions. No remediation write was attempted.
4. Scheduler background activity logged external Claude connection-refused
   failures while the app was running. This was not part of the Admin browser
   acceptance and no Specialist or Phase 7 acceptance was rerun.

These findings are retained as the initial Admin UI failures. They do not alter
the already recorded Specialist disposition and do not justify an architecture
change.

## 6. Corrective fixes and final revalidation

The two initial failures were product defects and were corrected with the
smallest scoped changes:

- `LOGOUT_CSRF_ROOT_CAUSE`: `AdminAuthMiddleware` checked only the CSRF header
  and query string, while the canonical HTML form submitted the token as an
  `application/x-www-form-urlencoded` body field.
- `LOGOUT_CSRF_FIX`: the middleware now reads only the form `csrf_token` field
  when no header/query token is present; POST remains required and the token
  is still validated against the authenticated session.
- `LOGOUT_SESSION_INVALIDATION`: the unchanged logout route revokes the
  session, clears the session cookie, and redirects to `/login` after valid
  form CSRF validation. Regression coverage confirms missing/invalid tokens
  return 403 and all three roles use the same canonical path.
- `LOGOUT_SECURITY = PASS`: logout remains POST-only, session-bound CSRF is
  required, invalid/missing tokens fail closed, unauthenticated logout is
  safe, and no session ID is exposed in the response.
- `REMEDIATION_RECURSION_ROOT_CAUSE`: the generic ORM serializer used the
  SQLAlchemy column key `metadata`, which resolved to declarative `MetaData()`
  instead of the model attribute `plan_metadata`; FastAPI then recursively
  encoded that framework object.
- `REMEDIATION_RECURSION_ENDPOINT`: the deterministic failing request was
  `GET /api/remediation?limit=500`, the exact request made by `/remediation`.
- `REMEDIATION_API_RECURSION_FIX`: the Admin remediation API now emits
  explicit finite read-model dictionaries for plans, approvals, executions,
  sandbox validations, and audit events. It does not traverse ORM mapper
  columns or return the declarative metadata object.
- `REMEDIATION_API_SERIALIZATION`: the frontend shape is preserved, including
  `plan_id`, lifecycle/risk fields, action/evidence IDs, and `plan_metadata`;
  missing plan detail remains a 404.

Final browser revalidation used the exact failed flows for viewer, operator,
and admin. Each role loaded `/remediation` with no `Unable to load data`,
`RecursionError`, or server error, then clicked the visible Logout form and
verified `/login` plus protected-route denial after logout. Browser console
error-level logs were empty. Admin System continued to report 25 registered
tools. No remediation write, execution, approval, sandbox mutation, or
production target was initiated.

No production orchestration defect was identified. The remediation change is
limited to Admin API serialization; remediation business logic and execution
semantics were not changed, so Phase 7 was not rerun.

### Final acceptance fields

`LOGOUT_MANUAL_REVALIDATION = PASS` (viewer/operator/admin);  
`REMEDIATION_MANUAL_REVALIDATION = PASS` (viewer/operator/admin);  
`RBAC_REGRESSION = PASS`; `CSRF_REGRESSION = PASS`;  
`REMEDIATION_REGRESSION = PASS`; `ADMIN_UI_FOCUSED_REGRESSION = PASS`;  
`BROWSER_CONSOLE = PASS`; `MCP_TOOL_COUNT = 25`;  
`CLAUDE_ADMIN_SEPARATION = PASS`; `COMPILEALL = PASS`;  
`GIT_DIFF_CHECK = PASS`; `ADMIN_UI_MANUAL_ACCEPTANCE = PASS`;  
`ADMIN_UI_PROJECT_CLOSURE_BLOCKING = NO`.

Changed production files: `app/interfaces/admin/auth.py` and
`app/interfaces/admin/api/remediation.py`. Changed regression files:
`tests/test_admin_auth_rbac.py` and `tests/test_admin_remediation_api.py`.
The focused command is recorded in the supporting verification above; the
manual scenarios were the exact failed Logout form and
`/remediation`/`GET /api/remediation?limit=500` flows for all three roles.
Core remediation orchestration logic was not changed and Phase 7 rerun was
not required. This record, `README.md`, and `10-final-project-readiness.md`
were updated; no commit or push occurred.

## 7. Supporting verification

- `AUTOMATED_ADMIN_REGRESSION = PASS`: 65 focused tests passed across
  `test_admin_auth_rbac.py`, `test_admin_remediation_api.py`,
  `test_admin_ui_completion.py`, `test_admin_system_web.py`,
  `test_admin_system_api.py`, `test_phase5_admin_api.py`,
  `test_phase5_supervised_remediation.py`, `test_phase6_sandbox_validation.py`,
  `test_route_inventory.py`, `test_project_mcp_tool_boundary.py`, and
  `test_claude_least_privilege.py`.
- `COMPILEALL = PASS`: `uv run --no-sync python -m compileall -q app tests`.
- `ROUTE_INVENTORY = PASS`: 99 FastAPI routes, 73 OpenAPI routes, and 26
  web-only routes were enumerated by `tools/dev/list_routes.py`.
- `MCP_TOOL_COUNT = 25`: confirmed in the Admin System / Safety UI and by the
  project catalog.
- `CLAUDE_ADMIN_SEPARATION = PASS`: focused least-privilege and tool-boundary
  tests passed; no Claude supervisor path was rerun.
- `DIFF_CHECK = PASS`: `git diff --check` completed without whitespace errors.
- Browser console diagnostics contained normal app/page-load logs and no
  JavaScript console errors. The initial Remediation failure was an HTTP/API
  response failure, not a browser console exception.

## 8. Final status

**PASS**

The two initial product defects were fixed and revalidated. No production
orchestration defect was identified, no architecture change is justified, and
no commit or push occurred.

**ADMIN_UI_PROJECT_CLOSURE_BLOCKING = NO**
