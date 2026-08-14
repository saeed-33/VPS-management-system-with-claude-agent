# AI VPS Management

`Safe Autonomous AI Agent for VPS Management` is an operational platform for
monitoring Linux VPS instances, investigating incidents, producing grounded
diagnoses, and applying only registered, policy-controlled remediation.
Claude Code supplies supervisory reasoning; Python remains authoritative for
validation, permissions, persistence, Evidence, SSH safety, and execution.

## Current status

```text
Phase 4.20: COMPLETE
C.14.0-C.14.11: COMPLETE
C.14.11A: PASS
C.14.12: PASS
C.14.13: PASS
C.14.14: PASS
Phase C: COMPLETE / CLOSED
Phase 5: COMPLETE / CLOSED
Phase 6: IMPLEMENTED / LIVE ACCEPTANCE EVIDENCE REQUIRES RECONCILIATION
Phase 7: IMPLEMENTED / LIVE ACCEPTANCE EVIDENCE NOT PRESENT IN REPOSITORY
automatic_remediation_allowed: false
provider: ollama
```

Phase 5 is closed. Phase 6 is implemented and has passing deterministic
coverage, but the repository contains conflicting live-acceptance records and
must not be described as closed until that evidence is reconciled. Phase 7 is
implemented and fail-closed, but no standalone live acceptance result is
stored in the repository. Automatic remediation remains disabled by default.

## Current architecture

```text
Claude Code       supervisory reasoning and sequencing
        |
Ollama            operational LLM provider
        |
vps MCP           bounded Claude-facing project tools
        |
Python            execution, validation, policy, persistence, evidence,
                  budgets, SSH safety, database access, and Admin/API
```

The invariant is:

```text
Claude decides WHAT / NEXT.
Python decides WHETHER ALLOWED and HOW IT IS EXECUTED SAFELY.
```

Canonical application packages and responsibilities are:

```text
app/core             contracts, configuration, policy, and safety rules
app/capabilities     monitoring, analysis, investigation, knowledge
app/runtime/claude   native Claude session, jobs, and observability
app/interfaces       Admin HTTP/Web and project MCP interfaces
app/infrastructure   PostgreSQL, SSH, and Ollama adapters
app/composition      dependency wiring and application bootstrap
```

The repository also contains `app/infrastructure/llm/ollama` for operational
LLM/embedding adapters, `app/infrastructure/ssh` for known-hosts SSH and
bounded named command execution, and `app/infrastructure/database` for the
PostgreSQL engine, models, repositories, and additive migrations.

## Repository tree

```text
app/core                         contracts, settings, policies, safety
app/capabilities                 monitoring, analysis, knowledge, investigation, remediation
app/runtime/claude               Claude sessions, jobs, parsing, observability
app/interfaces/admin             authenticated Admin API, Web UI, RBAC
app/interfaces/mcp               bounded Claude-facing MCP catalog and handlers
app/infrastructure/database      PostgreSQL models, repositories, migrations
app/infrastructure/ssh           known-hosts client and bounded command executor
app/infrastructure/llm/ollama    Ollama analysis, diagnosis, specialist, embedding adapters
app/composition                  dependency container and runtime wiring
tests                            unit, integration, security, recovery, UI, real opt-in tests
tools                            bootstrap, readiness, route, MCP, seed, and acceptance tools
docs                             canonical documentation, ADRs, operations, and report
```

Historical production trees `app/domain`, `app/admin`, `app/mcp`,
`app/shared`, and `app/tools` were removed.

## Operational workflow

```text
periodic monitoring
 -> Claude Code supervisory session
 -> Ollama model
 -> vps MCP
 -> monitoring capability
 -> persisted report
 -> exact or similar historical analysis
 -> persisted analysis
 -> optional Investigation
 -> dynamic DB-defined Specialists
 -> persisted Evidence
 -> final diagnosis
 -> bounded remediation proposal
 -> Claude-native isolated sandbox validation
 -> sandbox PASS
 -> persisted human approval
 -> registered named write
 -> verification or rollback
```

Automatic remediation execution is not enabled. Human-approved execution is
available only through the persisted approval and policy gates.

## Implemented capabilities

- bounded monitoring and report persistence;
- exact-match reuse and hybrid incident/knowledge retrieval;
- DB-defined Specialist selection and bounded investigation;
- fail-closed Evidence grounding and conflict preservation;
- policy and budget enforcement around diagnostic execution;
- known-hosts-verified SSH diagnostics;
- Claude AgentJob/session observability and restart recovery;
- Admin web/API surfaces for operational records;
- 25 bounded project MCP tools;
- deterministic and persisted runtime readiness evaluation.
- supervised remediation lifecycle with named service writes, approval
  fingerprints, idempotency, verification, rollback, and audit events;
- Admin remediation review/approval/execution/rollback surface;
- 13-metric Phase 5 readiness evaluator.
- Phase 6 fingerprint-bound isolated validation, project-owned Evidence,
  cleanup/restoration, fail-closed native-sandbox attestation, and 13-metric
  readiness evaluator.

## Safety model

Claude cannot use raw SSH, raw SQL, arbitrary shell, unrestricted filesystem
writes, or generic subprocess execution. Project tools are registered,
validated, policy-gated, budgeted, and return structured results. Unknown tools,
invalid Evidence references, provider failures, and missing approvals fail
closed. Automatic remediation remains disabled.

## Prerequisites and configuration

Required operational services are Python 3.14+, `uv`, PostgreSQL, Ollama with
the configured model, native Claude Code CLI for live runtime work, and a
managed VPS configuration with an SSH private key and `known_hosts` file.
Required settings are loaded from process environment first and `.env` as a
fallback. Do not store secrets in Git.

The important settings include `POSTGRES_*`, `OLLAMA_BASE_URL`,
`OLLAMA_MODEL`, `DEFAULT_SSH_PRIVATE_KEY_PATH`, `SSH_KNOWN_HOSTS_PATH`,
`LLM_PROVIDER=ollama`, `CLAUDE_RUNTIME_ENABLED`, and the explicit safety
switch `AUTOMATIC_REMEDIATION_ALLOWED` (default `false`).

See [runtime configuration](docs/operations/configuration.md) and
[startup operations](docs/operations/running-project.md) for exact settings.

## Database, migrations, and startup

```powershell
uv sync
uv run python tools/bootstrap_database.py
uv run python tools/bootstrap_database.py --verify-only
uv run uvicorn app.main:app --reload
```

The bootstrap creates the PostgreSQL database when authorized, enables
pgvector, creates SQLAlchemy tables and RAG indexes, and verifies the expected
33 tables and three custom RAG indexes. Additive SQL migrations are under
`app/infrastructure/database/migrations/`; they are applied by the project
database migration procedure before verification.

## Ollama, Claude Code, and MCP

Ollama is the only configured operational LLM provider. The default analysis
model is `qwen3:8b` and the default embedding model is `nomic-embed-text`;
the deployment may override them. Claude Code is an optional supervisory
runtime and uses the project `vps` MCP server. `.mcp.json` launches
`tools/run_project_mcp_server.py`; the server exposes exactly 25 registered
bounded tools. Claude is not given raw SSH, SQL, arbitrary shell, or
unrestricted filesystem capabilities.

## Admin UI

Start the application with the Uvicorn command above, then open
`http://127.0.0.1:8000/login`. Bootstrap the first Admin account with:

```powershell
uv run python tools/create_admin.py --username <name> --role admin
```

The command prompts for the password. Admin roles are `viewer`, `operator`,
and `admin`; the backend enforces permissions, CSRF, session expiry, and
audit events. `/runtime-policies` is only a compatibility redirect to the
current `/autonomous-runtime` screen.

## Development and testing

```powershell
uv sync
uv run python tools/bootstrap_database.py
uv run uvicorn app.main:app --reload
uv run python -m pytest
```

For the stable WSL test environment:

```bash
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system"
uv sync
uv run python -m pytest -q --ignore=tests/real_runtime
```

Health check: `http://127.0.0.1:8000/health`.

Real Claude/Ollama/MCP, Phase 5, Phase 6, and Phase 7 acceptance tests are
opt-in and require external infrastructure, a designated non-production
target, and explicit environment variables. Do not run them against
production. The normal suite does not execute live SSH or destructive
remediation.

Example Claude runtime opt-in:

```powershell
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="ollama"
$env:CLAUDE_RUNTIME_ENABLED="true"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="<server_id>"
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
uv run python -m pytest tests/real_runtime/test_c14_11_claude_ollama_mcp_acceptance.py -v -s
```

## Documentation

- [Current project status](docs/PROJECT_STATUS.md)
- [Canonical documentation map](docs/README.md)
- [Architecture overview](docs/architecture/overview.md)
- [Canonical architecture](docs/architecture/README.md)
- [Functional requirements](docs/requirements/functional-requirements.md)
- [Measurable NFRs](docs/requirements/non-functional-requirements.md)
- [Use cases](docs/use-cases/use-cases.md)
- [Project structure](docs/PROJECT_STRUCTURE.md)
- [Current workflows](docs/workflows/current-workflows.md)
- [Runtime configuration](docs/operations/configuration.md)
- [Running the project](docs/operations/running-project.md)
- [Claude runtime](docs/operations/claude-runtime.md)
- [Testing strategy](docs/testing/TESTING_STRATEGY.md)
- [Current test results](docs/testing/test-results.md)
- [C.14.12 readiness closeout](docs/architecture/steps/c14-12-runtime-readiness-gate.md)
- [Arabic technical report](docs/report/سعيد_بقدونس_هندسة_برمجيات_وذكاء_صنعي_Safe_Autonomous_AI_Agent_VPS.docx)

## Phase 6 acceptance state

Phase 5 is complete and closed on the designated non-production lab. Phase 6
and Phase 7 live-acceptance evidence must be reconciled from repository
records before they are reported as closed. Automatic remediation remains
disabled.
