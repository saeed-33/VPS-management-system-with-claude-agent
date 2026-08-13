# AI VPS Management

AI-assisted Linux VPS monitoring, investigation, and supervised diagnostic
operations. The application collects reports over verified SSH, persists
analysis and evidence in PostgreSQL, and exposes a bounded project MCP surface
to Claude Code.

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
Phase 6: IMPLEMENTED / NOT CLOSED
automatic_remediation_allowed: false
provider: ollama
```

Phase 5 is accepted and closed. Phase 6 is implemented but its readiness is
`blocked_by_sandbox_runtime` until real WSL2 Claude-native sandbox evidence is
available. Automatic remediation remains disabled.

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

Canonical application packages are:

```text
app/core             contracts, configuration, policy, and safety rules
app/capabilities     monitoring, analysis, investigation, knowledge
app/runtime/claude   native Claude session, jobs, and observability
app/interfaces       Admin HTTP/Web and project MCP interfaces
app/infrastructure   PostgreSQL, SSH, and Ollama adapters
app/composition      dependency wiring and application bootstrap
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
- 24 bounded project MCP tools;
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

## Runtime requirements

Required operational services are Python 3.14+, `uv`, PostgreSQL, Ollama with
the configured model, native Claude Code CLI, and a managed VPS configuration
with an SSH private key and `known_hosts` file. The project MCP server is
launched by `.mcp.json` through `tools/run_project_mcp_server.py`.

See [runtime configuration](docs/operations/configuration.md) and
[startup operations](docs/operations/running-project.md) for exact settings.

## Development and testing

```powershell
uv sync
uv run python tools/bootstrap_database.py
uv run uvicorn app.main:app --reload
uv run python -m pytest
```

Health check: `http://127.0.0.1:8000/health`.

The real Claude/Ollama/MCP acceptance is opt-in:

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
- [Architecture overview](docs/architecture/overview.md)
- [Project structure](docs/PROJECT_STRUCTURE.md)
- [Current workflows](docs/workflows/current-workflows.md)
- [Runtime configuration](docs/operations/configuration.md)
- [Running the project](docs/operations/running-project.md)
- [Claude runtime](docs/operations/claude-runtime.md)
- [Testing strategy](docs/testing/TESTING_STRATEGY.md)
- [C.14.12 readiness closeout](docs/architecture/c14-12-runtime-readiness-gate.md)

## Phase 6 acceptance state

Phase 5 is complete and closed on the explicitly designated non-production
`phase5-lab` target. Phase 6 is implemented but remains `PHASE 6 = NOT CLOSED`
until the opt-in Claude-native sandbox acceptance produces real WSL2 runtime
attestation and completes the safe validation flow. Automatic remediation
remains disabled.
