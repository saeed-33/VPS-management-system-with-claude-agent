# Claude, Ollama, and MCP Runtime

Claude Code is the supervisory runtime. `app/runtime/claude/supervisor.py`
handles the high-level session contract; `session_runner.py`, `runtime.py`,
`ollama_runtime.py`, and `result_parser.py` implement process and structured
result boundaries. `job_service.py` and `observability.py` persist AgentJob
and session telemetry.

The runtime uses Ollama as the operational provider. `app/infrastructure/llm/ollama/`
contains the analysis, final-diagnosis, Specialist-reasoning, and embedding
clients. `LLM_PROVIDER` is constrained to `ollama` by settings.

The project MCP server is started by `.mcp.json` through
`tools/run_project_mcp_server.py`. `ProjectMcpToolBoundary` exposes only the
catalogued project tools. The MCP layer serializes contracts; it does not
perform arbitrary execution or bypass Python policy.

```text
Claude Code
  -> supervisory prompt / bounded project MCP request
  -> app/interfaces/mcp/server.py
  -> ProjectMcpToolBoundary + typed handler
  -> capability service
  -> policy / Evidence / repository / bounded infrastructure
  -> structured result and audit/observability
```

Failure modes are controlled: disabled runtime, malformed model output,
provider timeout, MCP failure, invalid tool or invalid Evidence must return a
controlled failure rather than an unsafe fallback.

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
