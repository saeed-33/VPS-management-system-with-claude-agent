# Current Project Structure and Boundaries

This is the implemented C.14.11A architecture. There are no compatibility
packages under `app/domain`, `app/admin`, `app/mcp`, `app/shared`, or
`app/tools`.

```text
app/
├── core/            contracts, policies, configuration, exceptions
├── capabilities/    monitoring, analysis, investigation, knowledge
├── runtime/claude/  native Claude session/runtime integration
├── interfaces/
│   ├── mcp/         MCP server, registry, schemas, handlers
│   └── admin/       Admin API, web routes, templates, static assets
├── infrastructure/  database, SSH, and Ollama adapters
└── composition/     dependency wiring and bootstrap

tools/
├── run_project_mcp_server.py  .mcp.json stdio entry point
├── acceptance/                 runtime acceptance and evaluation
└── dev/                       inspection, seed, and documentation tools
```

## Responsibility and dependency rules

- `core` owns provider-neutral contracts, configuration, exceptions, utilities,
  and fail-closed policy. It does not import outer layers.
- `capabilities` owns bounded monitoring, analysis/RAG, investigation/evidence,
  and knowledge behavior. It does not import interfaces, composition, or the
  runtime.
- `runtime/claude` owns Claude CLI execution, stream decoding, and job
  lifecycle. Claude supplies supervisory sequencing; Python validates and
  executes capabilities.
- `interfaces/mcp` owns the single MCP registry/protocol server and the stable
  Claude-visible tool contract. Its handler implementations are grouped under
  `interfaces/mcp/handlers`.
- `interfaces/admin` owns HTTP routes, schemas, services, templates, and static
  assets. Admin observability reads the existing `agent_jobs` projection.
- `infrastructure/database` owns database engine/session/models/repositories;
  `infrastructure/ssh` is the only package importing `asyncssh`; and
  `infrastructure/llm/ollama` owns the configured LLM provider.
- `composition` wires the application and does not implement workflows.
- `tools/acceptance/evaluation` contains acceptance/readiness evaluation code;
  it is not imported by production application packages.

## Safety boundaries

Claude receives only bounded MCP tools. It has no raw SQL, raw SSH, unrestricted
shell, direct database, direct Ollama, or remediation-bypass capability. MCP
handlers call Python capabilities; policy, evidence, persistence, and approval
remain Python-owned. Automatic remediation remains disabled.

## Verification

The architecture tests enforce deleted legacy package trees, canonical import
ownership, layer dependency rules, and an acyclic application import graph.
The final C.14.11A report records the full suite and real Claude/Ollama/MCP
acceptance results.
