# 06 — Fresh-start / README Smoke Test

## 1. Objective

Prove that a fresh operator can follow the README and startup instructions to
install, configure, initialize, start, and health-check the project.

## 2. Scope

Fresh environment setup, dependency installation, database bootstrap, service
startup, health check, and the first safe read-only request.

## 3. Preconditions

Use an isolated dependency environment outside the repository and sanitized
development configuration. Do not repair or recreate the repository-local
`.venv`; on WSL use `UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system"`.
Real Phase 5/6/7/Specialist acceptance is outside this smoke test.

## 4. Environment

- Date: 2026-08-14.
- Repository: `E:\AI_VPS_Mamgment\chat_system`.
- Clean dependency environment:
  `C:\Users\SAEED\AppData\Local\Temp\chat-system-fresh-start-env`.
- Python: 3.14.3; `uv`: 0.11.30.
- The repository-local `.venv` was not used or modified.
- PostgreSQL and Ollama used the existing local development configuration;
  secrets and password values were not recorded.

## 5. Safety constraints

Do not copy secret values into documentation or command history. Keep the smoke
test read-only after initialization.

## 6. Exact commands or procedure

Dependency resolution and installation:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "C:\Users\SAEED\AppData\Local\Temp\chat-system-fresh-start-env"
uv sync --locked --no-install-project
```

Clean import and composition smoke:

```powershell
uv run --no-sync python -c "import app; from app.composition import container; print('CLEAN_IMPORT_SMOKE=PASS'); print(len(container.project_mcp_tool_boundary.list_tools()))"
```

Database setup/verification:

```powershell
uv run --no-sync python tools/bootstrap_database.py --skip-create-database
uv run --no-sync python tools/bootstrap_database.py --verify-only
```

The canonical bootstrap verified pgvector, 33/33 tables, and 3/3 custom RAG
indexes. The project exposes 16 additive SQL migration/reference files; the
fresh database path is the bootstrap script rather than a separate migration
runner.

Required definitions:

```powershell
uv run --no-sync python tools/dev/seed_specialists.py
```

The command was run twice; both runs exited successfully and skipped all 9
already-present definitions, proving the documented seed is idempotent. The
optional `--update-existing` mode is documented for intentional refreshes.

Admin bootstrap:

```powershell
uv run --no-sync python -m tools.create_admin --username <name> --role admin
```

The canonical tool was executed with a generated temporary password that was
never recorded. It created a local Admin account successfully.

Application startup used the documented Uvicorn composition with an isolated
smoke-test port:

```powershell
uv run --no-sync uvicorn app.main:app --host 127.0.0.1 --port 8010
```

The documented default port remains 8000; 8010 avoided an occupied local
listener during this acceptance.

## 7. Expected acceptance gates

The documented setup completes without undocumented local fixes, the service
starts, health checks pass, and a safe read-only request succeeds.

## 8. Actual results

```text
README_COMPLETENESS = PASS
PREREQUISITES_DOCUMENTATION = PASS
ENVIRONMENT_DOCUMENTATION = PASS
CLEAN_DEPENDENCY_RESOLUTION = PASS
CLEAN_IMPORT_SMOKE = PASS
FRESH_DATABASE_SETUP = PASS
REQUIRED_SEEDING = PASS
FRESH_ADMIN_BOOTSTRAP = PASS
FRESH_APP_STARTUP = PASS
FRESH_HTTP_SMOKE = PASS
OLLAMA_STARTUP_SMOKE = PASS
MCP_STARTUP_SMOKE = PASS
MCP_TOOL_COUNT = 25
CLAUDE_ADMIN_SEPARATION = PASS
FRESH_SAFE_DEFAULTS = PASS
DOCUMENTED_TEST_COMMANDS = PASS
README_LINK_AUDIT = PASS
PORTABILITY_AUDIT = PASS

FRESH_START_ACCEPTANCE = PASS
PROJECT_CLOSURE_BLOCKING = NO
COMPILEALL = PASS
GIT_DIFF_CHECK = PASS
```

The app reached `/health` with HTTP 200. `/login` returned HTTP 200, the fresh
Admin login redirected successfully, and `/`, `/servers`, `/investigations`,
`/remediation`, `/autonomous-runtime`, `/audit`, and `/system` each returned
HTTP 200. Ollama `gemma4:e4b-it-q4_K_M` was reachable, present, and answered a
minimal non-Specialist request. The MCP stdio server initialized and returned
25 tools.

## 9. Evidence / IDs

- Local URL: `http://127.0.0.1:8010/login` during the smoke run.
- Health endpoint: `GET http://127.0.0.1:8010/health` -> 200.
- Database schema: 33/33 tables, 3/3 custom RAG indexes, pgvector PASS.
- Specialist definitions: 9 present; repeated seed skipped 9/9.
- MCP catalog: 25 tools.
- Ollama model: `gemma4:e4b-it-q4_K_M`.

## 10. Failed attempts

The repository-local Windows `.venv` remains unusable because its `lib64`
junction can produce DrvFS/Windows access errors. It was not repaired or used;
the clean temporary environment completed successfully.

## 11. Root cause if failure occurred

No application or setup failure occurred in the clean environment. The only
environment limitation was the known repository-local `.venv` filesystem issue.

## 12. Fix performed

Corrected the root README and operational/testing documentation to describe
basic versus full-runtime prerequisites, the stable WSL environment, the
canonical bootstrap and Specialist seed commands, current acceptance state,
and the final-acceptance documentation entry point. No production code or
architecture was changed.

## 13. Revalidation

Dependency installation, import, database bootstrap/verification, seeding,
Admin bootstrap, application startup, login, HTTP page smoke, Ollama health and
minimal invocation, MCP initialization, and documentation link/path checks all
passed. Real Phase 5/6/7/Specialist acceptance was not rerun.

## 14. Remaining operator requirements

New deployments still require the operator to supply PostgreSQL credentials,
an external production Admin session secret, secure-cookie/HTTPS settings,
SSH key and `known_hosts` paths when monitoring is enabled, and an Ollama model
when LLM capabilities are enabled. Claude, a managed VPS, and WSL2 sandbox
attestation are required only for their respective real acceptance/runtime
workflows.

## 15. Final status

**FRESH_START_ACCEPTANCE = PASS**

**PROJECT_CLOSURE_BLOCKING = NO**

## 16. Whether production code changed

No production code or architecture changed for this acceptance record. Only
README, operational/testing documentation, and final-acceptance records were
updated.

## 17. Whether commit/push occurred

No commit or push occurred.
