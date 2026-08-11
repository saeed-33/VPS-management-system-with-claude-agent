# RAG Rule

Incident RAG and Knowledge RAG are separate project-owned retrieval systems.

Claude Code must not reimplement embeddings, pgvector/HNSW, full-text search,
RRF fusion, compatibility checks, source attribution, or provenance validation
inside prompts.

Historical report workflow:

```text
search exact match first
 -> exact match: reuse previous analysis
 -> otherwise search similar historical reports
 -> pass at most top 3 similar reports to the LLM context
```

Incident history is context, not proof of current server state. Technical
knowledge can explain behavior, but live operational claims require Evidence.

All LLM analysis must route through project services using Ollama when tools
exist.
