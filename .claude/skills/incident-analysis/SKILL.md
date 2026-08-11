# Incident Analysis Skill

Use this skill when a monitoring report needs reuse, retrieval, or LLM-backed
analysis.

## Boundaries

Incident RAG and LLM analysis are owned by Python services. Ollama is the
operational LLM provider.

## Required workflow

```text
load current report
search exact historical match
if exact match exists: reuse previous analysis
otherwise search similar reports
pass top 3 similar reports to project analysis
read persisted analysis
```

Historical reports are context. Current server facts require current report data
or Evidence.
