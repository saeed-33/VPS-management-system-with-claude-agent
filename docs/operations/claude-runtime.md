# Claude Code Runtime Operations

<!-- DOC-STATUS: CURRENT -->

## Contract

The active runtime contract is:

```text
Claude Code      supervisory reasoning and sequencing
Ollama           operational model provider
server-supervisor main bounded per-server agent
specialist-worker bounded DB-defined Specialist worker
vps MCP          25 project capability tools
Python           execution, policy, evidence, budgets, persistence, safety
```

Canonical runtime packages are `app\runtime\claude` and
`app\interfaces\mcp`; the Admin adapter is under `app\interfaces\admin`.

Claude decides WHAT/NEXT. Python decides WHETHER ALLOWED and HOW EXECUTED
SAFELY. Claude does not receive raw SSH, raw SQL, arbitrary shell, unrestricted
filesystem access, or generic subprocess access.

## Project configuration

The Settings default is `OLLAMA_MODEL=qwen3:8b`; prepare it with:

```powershell
ollama pull qwen3:8b
```

The accepted C.14.12 operational run used `gemma4:e4b-it-q4_K_M` instead.

The native Claude CLI is launched through the project runtime with:

- `CLAUDE_RUNTIME_ENABLED` feature flag;
- `CLAUDE_RUNTIME_EXECUTABLE`, normally `claude`;
- `CLAUDE_RUNTIME_OLLAMA_EXECUTABLE`, normally `ollama`;
- effective model from `CLAUDE_RUNTIME_MODEL` or `OLLAMA_MODEL`;
- `CLAUDE_RUNTIME_AGENT=server-supervisor`;
- bounded timeout and turn limits;
- strict project MCP configuration from `.mcp.json`.

The project runtime uses an Ollama-backed Claude-compatible transport. It does
not use an Anthropic-hosted reasoning model. Do not use
`--dangerously-skip-permissions`; it is not an accepted project runtime method.

## Agents and Skills

The project contracts are:

```text
.claude/agents/server-supervisor.md
.claude/agents/specialist-worker.md
.claude/skills/monitor-server/SKILL.md
.claude/skills/analyze-incident/SKILL.md
.claude/skills/investigate-incident/SKILL.md
.claude/skills/plan-remediation/SKILL.md
```

`server-supervisor` owns high-level sequencing for one server and may use
project MCP tools. `specialist-worker` executes one bounded DB-defined
Specialist task and cannot delegate. Skills describe the current workflow and
must not bypass project tools, policy, Evidence, or budgets.

## MCP

`.mcp.json` registers the `vps` server through
`tools/run_project_mcp_server.py`. The registry exposes exactly 25 tools in
monitoring, reports, retrieval, investigation, Specialists, and bounded
plan-remediation workflow. Non-read-only tools remain policy-gated and no
production remediation is automatically applied.

## Runtime observability

Each supervisory run creates an AgentJob and records Claude session ID, status,
turns, tool calls, MCP status, duration, usage metadata, and errors. Runtime
snapshots persist report, analysis, investigation, Specialist, Evidence,
conflict, and diagnosis state. Application startup recovers queued/running jobs
interrupted by restart into a deterministic failed state.

## Runtime acceptance

```powershell
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="ollama"
$env:CLAUDE_RUNTIME_ENABLED="true"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="<server_id>"
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
uv run --no-sync python -m pytest tests/real_runtime/test_c14_11_claude_ollama_mcp_acceptance.py -v -s
```

The test is intentionally opt-in because it requires PostgreSQL, Ollama,
Claude CLI, MCP, SSH credentials, and a reachable managed server.

## Failure behavior

Claude, Ollama, MCP, database, SSH, policy, Evidence, and budget failures are
reported as structured failures and stop the affected operation. The runtime
does not fabricate a healthy result or fall back to unrestricted execution.

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
