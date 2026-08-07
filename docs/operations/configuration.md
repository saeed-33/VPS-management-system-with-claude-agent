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

Validation: Assisted يتطلب Vector؛ Full-Text حاليًا يتطلب Vector؛ و`RAG_CONTEXT_TOP_K <= RAG_TOP_K`.

## Embedding
`EMBEDDING_PROVIDER=ollama`, `OLLAMA_EMBEDDING_MODEL=nomic-embed-text`,
`EMBEDDING_DIMENSIONS=768`, `EMBEDDING_TIMEOUT_SECONDS=60`.

## LLM
`LLM_ENABLED=false`, `LLM_PROVIDER=ollama`, timeout=120s،
`LLM_MAX_REPORT_CHARACTERS=50000`, `OLLAMA_MODEL=qwen3:8b`,
`OPENAI_MODEL=gpt-5-mini`.

## Monitoring/SSH
polling=5s، default monitor interval=60s، command timeout=20s،
SSH connect timeout=15s، max concurrent servers=5، queue/server=100.

## Database
يلزم PostgreSQL host/port/db/user/password. الإعدادات تقرأ من `.env`.
