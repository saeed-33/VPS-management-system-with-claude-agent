# C.14.11A.4.2d — Runtime Composition

Monitoring, MCP, Claude/Ollama runtime, and scheduler construction now live in
`app/composition/runtime.py`.

The main builder is reduced to composition coordination:

1. repositories
2. deterministic core services
3. retrieval/RAG/PDF
4. admin SSH test service
5. analysis/investigation
6. runtime composition
7. `ApplicationContainer`

The Claude-visible MCP contracts and tool names are unchanged. Claude continues
to decide WHAT/NEXT while Python remains responsible for policy enforcement and
safe execution.
