# C.14.11 Real Claude/Ollama/MCP acceptance

C.14.11 converts the proven manual runtime smoke into an explicit,
repeatable acceptance test.

## Separation from the normal test suite

The real-runtime test is collected by pytest but skipped unless:

```powershell
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="ollama"
$env:CLAUDE_RUNTIME_ENABLED="true"
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="2"
```

This prevents ordinary unit/regression tests from invoking Ollama, Claude
Code, MCP, SSH monitoring, or production-like persistence.

## Preconditions

- `LLM_ENABLED=true`
- `LLM_PROVIDER=ollama`
- `CLAUDE_RUNTIME_ENABLED=true`
- the configured Claude executable is available on PATH;
- Ollama is running and exposes the configured model through the
  Anthropic-compatible endpoint;
- the project `vps` MCP server is configured;
- the selected server exists in the project database;
- the Ollama runtime has sufficient context for Claude Code. C.14.7
  accepted `OLLAMA_CONTEXT_LENGTH=65536`.

## Acceptance evidence

A PASS requires one real Claude-native monitoring session to produce:

1. a completed Claude agent job with a non-empty Claude session ID;
2. `vps` MCP reported as connected;
3. actual `mcp__vps__run_monitoring` tool evidence;
4. actual `mcp__vps__analyze_report` tool evidence;
5. a new persisted monitoring report for the selected server;
6. a completed persisted analysis for that exact report;
7. a C.14.10 observability trace that verifies mandatory tools and MCP;
8. when Claude starts an investigation, a persisted investigation attached
   to that exact report.

The test does not require a healthy server. Connection failures and critical
health are valid monitoring outcomes if they are honestly persisted and
analyzed. It tests the orchestration/runtime contract, not server health.

## Run

First validate the non-live contract:

```powershell
uv run python -m pytest tests	est_c14_11_runtime_contract.py
```

Then execute the real acceptance:

```powershell
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="2"

uv run python -m pytest -s `
  tests
eal_runtime	est_c14_11_claude_ollama_mcp_acceptance.py
```

Finally clear only the opt-in flag if desired:

```powershell
Remove-Item Env:AI_VPS_RUN_REAL_RUNTIME_TESTS
Remove-Item Env:AI_VPS_REAL_RUNTIME_SERVER_ID
```
### Pytest database isolation

The opt-in real-runtime test explicitly reloads `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` from the project `.env` before importing the application container. This is intentional: the normal pytest environment may inject isolated test-database credentials, while C.14.11 must exercise the same persistence configuration used by the operational application.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
