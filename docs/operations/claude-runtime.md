# Running the Project with Claude

## Prerequisites

```text
PostgreSQL is running and migrated.
Ollama is running.
Required Ollama models are pulled.
Claude Code is installed and authenticated.
Project dependencies are installed with uv.
```

## Ollama

Start Ollama, then pull the configured models:

```powershell
ollama serve
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

The project configuration uses Ollama for analysis and embeddings:

```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## Application

Install dependencies:

```powershell
uv sync
```

Apply database migrations or bootstrap a new database according to
`docs/operations/database-bootstrap.md`.

Start the API and scheduler:

```powershell
uv run uvicorn app.main:app --reload
```

Check runtime status:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected supervisor section:

```json
{
  "runtime": "claude",
  "state": "active"
}
```

## Claude Code

Start Claude Code from the repository root:

```powershell
cd E:\AI_VPS_Mamgment\chat_system
claude
```

Claude loads:

```text
CLAUDE.md
.mcp.json
.claude/settings.json
.claude/rules/
.claude/commands/
.claude/skills/
.claude/agents/
.claude/hooks/
```

The repository registers the project-scoped MCP server in `.mcp.json`:

```text
vps -> uv run python tools/run_project_mcp_server.py
```

Claude Code uses that server to call project tools as `mcp__vps__*`. Direct
SSH, SQL, remediation, or Ollama calls outside project tools are not part of
the runtime contract.

Useful checks:

```powershell
Get-Content .mcp.json
Get-Content .claude\settings.json
Get-Content .claude\agents\monitoring-supervisor.md
```

## Verification

Run:

```powershell
uv run python -m pytest
uv run python -m compileall app\admin app\domain app\runtime app\mcp app\shared app\tools tools tests app\bootstrap.py app\main.py
uv run python tools\sync_documentation.py
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
