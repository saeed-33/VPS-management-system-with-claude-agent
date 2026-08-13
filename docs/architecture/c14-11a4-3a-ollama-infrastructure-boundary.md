# C.14.11A.4.3a — Ollama Infrastructure Boundary

Provider-specific Ollama implementations are moved out of the domain tree into:

- `app/infrastructure/llm/ollama/analysis_client.py`
- `app/infrastructure/llm/ollama/embedding_client.py`

Provider-neutral contracts remain at their historical locations for now.
Historical Ollama modules remain thin compatibility facades until A.4.6.
