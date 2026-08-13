# AI VPS Management

AI-assisted Linux VPS monitoring and investigation through SSH, Ollama-backed
analysis, Claude-native supervision, a project MCP server, and a browser Admin
interface. Production remediation remains disabled and policy/user-gated.

## Current status

```text
Phase 4.20: complete
C.14.0–C.14.11: implemented and accepted
C.14.11A: complete
C.14.12: next, not started
Phase 5: blocked pending C.14.12 and later gates
automatic_remediation_allowed: false
llm_provider: ollama
```

The current implementation keeps Python responsible for execution, persistence,
policy, evidence, RAG, SSH, and Admin/API surfaces. Claude Code is the intended
supervisory runtime and sees the stable project MCP contract through
`.mcp.json`.

## Architecture

```text
app/core            contracts, policies, configuration
app/capabilities    analysis, investigation, knowledge, monitoring
app/infrastructure  database, SSH, Ollama, external adapters
app/interfaces      Admin HTTP/Web and Claude MCP interfaces
app/runtime         Claude session/runtime integration
app/composition     dependency wiring and application bootstrap
tools/acceptance    runtime acceptance and evaluation entry points
tools/dev           documentation, inspection, seed, and developer tools
```

The canonical project MCP entry point is:

```text
tools/run_project_mcp_server.py
```

It is referenced by `.mcp.json`; do not move it without updating that contract.

## Running locally

```powershell
uv run python -m pytest
uv run python tools/acceptance/run_all_tests.py --mode full
uv run python tools/acceptance/run_all_tests.py --mode readiness --limit 500
```

Useful developer commands:

```powershell
uv run python tools/dev/generate_test_catalog.py
uv run python tools/dev/generate_project_structure.py
uv run python tools/dev/sync_documentation.py
uv run python tools/dev/audit_documentation.py
```

For real Claude/Ollama/MCP acceptance, see
`docs/testing/TESTING_STRATEGY.md` and
`docs/testing/multi-agent-test-methodology.md`.

## Documentation

- [Current project status](docs/PROJECT_STATUS.md)
- [Architecture overview](docs/architecture/overview.md)
- [Target project structure](docs/architecture/target-project-structure.md)
- [Testing strategy](docs/testing/TESTING_STRATEGY.md)
- [Generated project structure](docs/PROJECT_STRUCTURE.md)
