# analyze

Purpose: supervise report reuse/retrieval and analysis through project-owned
tools.

Required sequence:

```text
get report
search exact historical match
if exact match exists: reuse previous analysis
otherwise search similar historical reports
pass at most top 3 similar reports to project LLM analysis
read persisted analysis
```

LLM analysis must route through the configured Ollama project client.
