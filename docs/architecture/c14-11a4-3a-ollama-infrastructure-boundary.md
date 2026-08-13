# C.14.11A.4.3a — Ollama Infrastructure Boundary

> Historical migration record. C.14.11A structural closure removed the
> temporary compatibility modules mentioned by this migration.

Provider-specific Ollama implementations live under:

- `app/infrastructure/llm/ollama/analysis_client.py`
- `app/infrastructure/llm/ollama/embedding_client.py`

Provider-neutral contracts live in `app/core` and capability-owned modules.
The historical Ollama facades are no longer present.
