# Running the Project

<!-- DOC-STATUS: CURRENT -->

## 1. Install dependencies

From the repository root:

```powershell
uv sync
```

For WSL, keep the project environment on the Linux filesystem rather than
under `/mnt/e`:

```bash
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system"
uv sync
```

Python 3.14+ is required by `pyproject.toml`.

## 2. Configure services

Copy `.env.example` to `.env` and set PostgreSQL credentials, SSH private-key
and `known_hosts` paths, Ollama model settings, and monitoring values. Start
PostgreSQL and Ollama. Verify the native Claude CLI is available:

```powershell
claude --version
ollama list
```

Install the model named by `OLLAMA_MODEL` (or `CLAUDE_RUNTIME_MODEL`) in the
local Ollama instance.

For local HTTP development, explicitly set `DEBUG=true` and
`ADMIN_SESSION_SECURE=false`. For production-like deployment, set
`DEBUG=false`, provide a stable external `ADMIN_SESSION_SECRET` of at least
32 characters, set `ADMIN_SESSION_SECURE=true`, and place the application
behind an HTTPS reverse proxy.

## 3. Prepare PostgreSQL

For a new database:

```powershell
uv run --no-sync python tools/bootstrap_database.py
```

The application creates/checks its tables during startup as well. Use the
bootstrap command when creating a new operational database or when explicit
database preparation is needed.

Seed the required DB-defined Specialists idempotently:

```bash
uv run --no-sync python tools/dev/seed_specialists.py
```

## 4. Start the application

```powershell
uv run --no-sync uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For local HTTP development only, `DEBUG=true` and `--reload` may be used
explicitly. Production-like startup uses `DEBUG=false`, a stable external
`ADMIN_SESSION_SECRET`, `ADMIN_SESSION_SECURE=true`, and an HTTPS reverse
proxy.

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The Admin web interface is served at `http://127.0.0.1:8000/`. The JSON API is
under `/api`; AgentJob observability is under
`/api/agent-observability/summary` and `/api/agent-observability/jobs`.

## 5. MCP entrypoint

Claude Code loads the project MCP server from `.mcp.json`. The direct entrypoint
for inspection or protocol use is:

```powershell
uv run --no-sync python tools/run_project_mcp_server.py
```

The server name is `vps` and the catalog contains 25 bounded project tools.

## 6. Real runtime acceptance

Real acceptance is opt-in and requires a reachable managed server, operational
PostgreSQL, Ollama, native Claude CLI, SSH credentials, and MCP:

```powershell
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="ollama"
$env:CLAUDE_RUNTIME_ENABLED="true"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="<server_id>"
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
uv run --no-sync python -m pytest tests/acceptance/external_runtime/test_real_claude_ollama_mcp_cycle.py -v -s
```

The test persists a real AgentJob/session outcome and verifies report, analysis,
MCP, and controlled failure/success semantics. Do not run it against an
unapproved production target.

## 7. Normal tests

```powershell
uv run --no-sync python -m pytest
```

See [TESTING_STRATEGY.md](../testing/TESTING_STRATEGY.md) for the required
focused, controlled, persisted, and real-runtime validation layers.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
