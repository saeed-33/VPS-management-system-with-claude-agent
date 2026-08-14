# Runtime Configuration

<!-- DOC-STATUS: CURRENT -->

Configuration is loaded by `app/core/config.py` from the project `.env` file
using case-insensitive environment names. Copy `.env.example` to `.env` and
replace credentials and paths. Never commit the real `.env`.

## Required

These settings must be supplied for a normal application instance:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DEFAULT_SSH_PRIVATE_KEY_PATH
SSH_KNOWN_HOSTS_PATH
```

The PostgreSQL database must be reachable and the SSH private key and
`known_hosts` file must be readable by the application. Managed VPS records
provide the target host, user, port, and monitoring configuration.

## PostgreSQL

```text
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=<database>
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<secret>
DATABASE_ECHO=false
```

The application uses PostgreSQL through `psycopg`, SQLModel/SQLAlchemy,
`pgvector`, and the repository layer. Prepare a new database with:

```powershell
uv run python tools/bootstrap_database.py
```

## SSH and monitoring

```text
DEFAULT_SSH_PRIVATE_KEY_PATH=C:/Users/USER/.ssh/id_ed25519
SSH_KNOWN_HOSTS_PATH=C:/Users/USER/.ssh/known_hosts
SSH_CONNECT_TIMEOUT_SECONDS=15
COMMAND_TIMEOUT_SECONDS=20
MONITOR_POLLING_INTERVAL_SECONDS=5
DEFAULT_MONITOR_INTERVAL_SECONDS=60
MAX_CONCURRENT_SERVERS=5
```

The SSH client enforces private-key validation and `known_hosts` verification.
Command execution is bounded by `COMMAND_TIMEOUT_SECONDS`.

## Ollama analysis and Claude runtime

```text
LLM_ENABLED=true
LLM_PROVIDER=ollama
LLM_ANALYSIS_TIMEOUT_SECONDS=120
LLM_MAX_REPORT_CHARACTERS=50000
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b
CLAUDE_RUNTIME_ENABLED=false
CLAUDE_RUNTIME_MODEL=gemma4:e4b-it-q4_K_M
CLAUDE_RUNTIME_TIMEOUT_SECONDS=300
CLAUDE_RUNTIME_MAX_TURNS=20
CLAUDE_RUNTIME_OLLAMA_EXECUTABLE=ollama
CLAUDE_RUNTIME_EXECUTABLE=claude
CLAUDE_RUNTIME_AGENT=server-supervisor
```

`LLM_PROVIDER` and `EMBEDDING_PROVIDER` are restricted to `ollama`. The
Settings default is `qwen3:8b`; the accepted C.14.12 operational `.env` used
`gemma4:e4b-it-q4_K_M`. The Claude
runtime requires `LLM_ENABLED=true`, `LLM_PROVIDER=ollama`, and a non-empty
effective model. `CLAUDE_RUNTIME_MODEL` may be empty to reuse `OLLAMA_MODEL`.

Required runtime binaries are the native `claude` CLI and the Ollama
executable. The accepted C.14.12 runtime used model
`gemma4:e4b-it-q4_K_M`; use a model installed in the local Ollama instance.

## Retrieval and embeddings

```text
RAG_EXACT_REUSE_ENABLED=true
RAG_VECTOR_ENABLED=true
RAG_ASSISTED_ENABLED=true
RAG_STRUCTURED_COMPATIBILITY_ENABLED=true
RAG_FULL_TEXT_ENABLED=true
RAG_FULL_TEXT_CANDIDATE_LIMIT=20
RAG_FULL_TEXT_MINIMUM_RANK=0.0
RAG_MINIMUM_SIMILARITY=0.72
RAG_CONTEXT_TOP_K=3
RAG_RRF_K=60
RAG_HNSW_EF_SEARCH=100
RAG_TOP_K=5
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
EMBEDDING_TIMEOUT_SECONDS=60
```

Vector retrieval is required when assisted or full-text retrieval is enabled.

## Optional application settings

```text
APP_NAME=AI VPS Management
DEBUG=true
PDF_FONT_PATH=<optional project font path>
```

## Test-only and acceptance-only settings

Normal pytest configuration supplies isolated PostgreSQL test settings and
disables the Claude runtime. Real acceptance is opt-in and uses the project
`.env` operational database settings:

```text
AI_VPS_RUN_REAL_RUNTIME_TESTS=1
AI_VPS_REAL_RUNTIME_SERVER_ID=<managed server id>
```

The real test also requires `LLM_ENABLED=true`, `LLM_PROVIDER=ollama`,
`CLAUDE_RUNTIME_ENABLED=true`, Ollama, Claude CLI, PostgreSQL, MCP, and a
reachable managed server.

## MCP configuration

`.mcp.json` registers one server named `vps` and launches:

```text
uv run --no-sync --project ${CLAUDE_PROJECT_DIR:-.} python
${CLAUDE_PROJECT_DIR:-.}/tools/run_project_mcp_server.py
```

The MCP server is project-scoped and exposes exactly 25 bounded tools.

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
