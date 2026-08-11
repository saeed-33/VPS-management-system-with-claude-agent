# Configuration Reference

## RAG

| Setting | Default |
|---|---:|
| `RAG_EXACT_REUSE_ENABLED` | true |
| `RAG_VECTOR_ENABLED` | true |
| `RAG_ASSISTED_ENABLED` | true |
| `RAG_STRUCTURED_COMPATIBILITY_ENABLED` | true |
| `RAG_FULL_TEXT_ENABLED` | true |
| `RAG_FULL_TEXT_CANDIDATE_LIMIT` | 20 |
| `RAG_FULL_TEXT_MINIMUM_RANK` | 0.0 |
| `RAG_MINIMUM_SIMILARITY` | 0.72 |
| `RAG_CONTEXT_TOP_K` | 3 |
| `RAG_RRF_K` | 60 |
| `RAG_HNSW_EF_SEARCH` | 100 |
| `RAG_TOP_K` | 5 |

Validation:

```text
RAG_ASSISTED_ENABLED requires RAG_VECTOR_ENABLED
RAG_FULL_TEXT_ENABLED currently requires RAG_VECTOR_ENABLED
RAG_CONTEXT_TOP_K must be <= RAG_TOP_K
```

## Embedding

```text
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
EMBEDDING_TIMEOUT_SECONDS=60
```

## LLM

Defaults:

```text
LLM_ENABLED=false
LLM_PROVIDER=ollama
LLM_ANALYSIS_TIMEOUT_SECONDS=120
LLM_MAX_REPORT_CHARACTERS=50000
OLLAMA_MODEL=qwen3:8b
OPENAI_MODEL=gpt-5-mini
```

Operational decision:

```text
Ollama is the project LLM provider for report analysis, assisted RAG analysis,
specialist reasoning, and final synthesis.
```

Claude Code supervises orchestration and must invoke project tools that use the
configured Ollama clients instead of bypassing them.

## Monitoring/SSH

```text
MONITOR_POLLING_INTERVAL_SECONDS=5
DEFAULT_MONITOR_INTERVAL_SECONDS=60
COMMAND_TIMEOUT_SECONDS=20
SSH_CONNECT_TIMEOUT_SECONDS=15
MAX_CONCURRENT_SERVERS=5
LLM_ANALYSIS_QUEUE_SIZE_PER_SERVER=100
```

## Database

PostgreSQL host, port, database, user, and password are required. Settings are
loaded from `.env`.

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

## Next Phase

```text
Phase C - Claude Code Supervisory Runtime
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution
see `docs/testing/TESTING_STRATEGY.md`.

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
