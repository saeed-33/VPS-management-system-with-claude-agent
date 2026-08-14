# 05 — Deployment Security Acceptance

## 1. Objective

Verify that deployment, configuration, authentication, SSH, database, least
privilege, and fail-closed security controls are ready for the intended target.

## 2. Scope

Deployment checklist, systemd/container configuration, secret handling,
known-hosts validation, network exposure, Admin authorization, and default
remediation safety.

## 3. Preconditions

Use the local repository as authoritative and a sanitized non-production
configuration. Inspect environment variable names and file permissions without
exposing secret values. This audit did not rerun real Phase 5, Phase 6, Phase 7,
or Specialist acceptance.

## 4. Environment

The audit was performed on 2026-08-14 in the local Windows worktree at
`E:\AI_VPS_Mamgment\chat_system`. Configuration, startup, deployment
documentation, authentication, SSH, MCP boundaries, logging, and security
tests were inspected. Non-real tests ran in the isolated
`.codex-test-venv` environment because the repository `.venv` is not usable on
this Windows host. Supporting material is in
[`production-checklist.md`](../deployment/production-checklist.md) and
[`security-baseline.md`](../security/security-baseline.md).

## 5. Safety constraints

Never print passwords, private-key contents, tokens, cookies, or database
password values. Keep automatic remediation disabled unless a narrowly scoped
acceptance procedure explicitly requires it.

## 6. Exact commands or procedure

- Inspected startup/configuration defaults, the Admin session and CSRF
  boundary, deployment topology, database/Ollama defaults, SSH known-host
  validation, MCP tool definitions, Claude/Admin separation, and logging/auth
  audit fields.
- Scanned tracked files for private-key headers and common API/token formats;
  `.env` is ignored and `.env.example` contains placeholders only. No secret
  values were printed.
- Ran the focused deployment/auth/MCP/separation security suite:
  `.codex-test-venv\Scripts\python.exe -m pytest
  tests/test_deployment_security_config.py tests/test_admin_auth_rbac.py
  tests/test_admin_system_api.py tests/test_admin_system_web.py
  tests/test_phase7_negative_security.py tests/test_project_mcp_tool_boundary.py
  tests/test_claude_least_privilege.py
  tests/test_claude_project_mcp_runtime_config.py
  tests/test_phase7_acceptance_environment.py -q`.
- Ran the full non-real regression, compileall, and `git diff --check` after
  the documentation and configuration updates.

## 7. Expected acceptance gates

Deployment configuration is reproducible, secrets are externalized, access is
least-privilege, SSH is host-key validated, Admin/RBAC controls pass, and
unsafe autonomous behavior is disabled by default.

## 8. Actual results

The audit identified one real deployment blocker and corrected it: production
could previously start with `DEBUG=true` and an empty Admin session secret,
which caused a process-local fallback secret. The configuration now defaults
to `DEBUG=false`, requires an external `ADMIN_SESSION_SECRET` of at least 32
characters when debug is disabled, and requires `ADMIN_SESSION_SECURE=true` in
that mode. Development fallback remains available only under explicit
`DEBUG=true`.

No other real deployment-security defect was identified. The deployment model
keeps the app on loopback behind an HTTPS reverse proxy, keeps PostgreSQL and
Ollama internal, uses SSH private keys plus known-hosts validation, exposes
exactly 25 project-owned MCP tools, keeps autonomous remediation disabled by
default, and preserves the Claude/Admin boundary. Admin sessions are
HttpOnly, SameSite=Lax, CSRF-protected, expiry/revocation checked, and never
log secrets or token values.

```text
ADMIN_SESSION_SECRET_SECURITY = PASS
SESSION_COOKIE_SECURITY = PASS
HTTPS_DEPLOYMENT_MODEL = PASS
NETWORK_EXPOSURE_REVIEW = PASS
DATABASE_DEPLOYMENT_SECURITY = PASS
OLLAMA_DEPLOYMENT_SECURITY = PASS
MCP_DEPLOYMENT_BOUNDARY = PASS
CLAUDE_ADMIN_SEPARATION = PASS
DEBUG_BYPASS_AUDIT = PASS
AUTONOMY_SAFE_DEFAULT = PASS
SSH_DEPLOYMENT_SECURITY = PASS
SECRET_SCAN = PASS
LOGGING_SECRET_HYGIENE = PASS
WEB_REQUEST_SECURITY = PASS
ADMIN_BOOTSTRAP_SECURITY = PASS

DEPLOYMENT_SECURITY_ACCEPTANCE = PASS
PROJECT_CLOSURE_BLOCKING = NO
SECURITY_TESTS = 86 passed
FULL_NON_REAL_REGRESSION = 620 passed, 4 skipped (624 collected)
COMPILEALL = PASS
GIT_DIFF_CHECK = PASS
DOCUMENTATION_UPDATED = PASS
```

## 9. Evidence / IDs

- MCP tool count: `25`.
- Focused security and boundary suite: `86 passed`.
- Full non-real regression: recorded in Section 13 after completion.
- Configuration tests cover development fallback, missing/weak production
  secret rejection, secure-cookie enforcement, and valid production settings.
- No production execution path was changed, so real acceptance was not rerun.

## 10. Failed attempts

The audit found the unsafe production configuration default described in
Section 8. It was a deployment hardening defect, not an orchestration or
architecture defect, and was corrected before final verification.

## 11. Root cause if failure occurred

The prior settings allowed a development-oriented debug default and an empty
session secret in a production-like process. The corrected settings fail closed
when `DEBUG=false`.

## 12. Fix performed

Updated `app/core/config.py`, `.env.example`, deployment/operations
documentation, and the configuration security tests. No production
orchestration, MCP, Claude, Specialist, Phase 5, Phase 6, or Phase 7 execution
semantics were changed.

## 13. Revalidation

Focused security tests passed: `86 passed`. The full non-real regression passed:
`620 passed, 4 skipped` (`624 collected`). Compileall passed in the isolated
`.codex-test-venv`; the requested `uv run --no-sync` invocation was also
attempted but could not start because the repository `.venv\lib64` junction
returned Windows `Access is denied`. `git diff --check` passed. No real Phase
5/6/7/Specialist acceptance was rerun.

## 14. Remaining operator configuration requirements

Before production deployment, an operator must provision a stable random
`ADMIN_SESSION_SECRET` of at least 32 characters outside the repository, set
`DEBUG=false` and `ADMIN_SESSION_SECURE=true`, terminate TLS at the documented
HTTPS reverse proxy, keep PostgreSQL and Ollama on internal/private listeners,
provision SSH private keys and a maintained `known_hosts` file, and enforce
backup, log-permission, rotation, and credential-rotation procedures. These
are deployment inputs, not repository defects.

## 15. Final status

**DEPLOYMENT_SECURITY_ACCEPTANCE = PASS**

**PROJECT_CLOSURE_BLOCKING = NO**

## 16. Whether production code changed

Only deployment configuration validation changed: production now fails closed
without a strong external Admin session secret and secure cookie setting. No
production orchestration or architecture change was made.

## 17. Whether commit/push occurred

No commit or push occurred.
