# Current Project Structure and Boundaries

This document describes the implemented local architecture after C.14.11A.

```text
app/
├── core/
│   ├── contracts/
│   └── policies/
├── capabilities/
│   ├── monitoring/
│   ├── analysis/
│   ├── investigation/
│   ├── knowledge/
│   └── remediation/
├── runtime/claude/
├── interfaces/
│   ├── mcp/
│   └── admin/
├── infrastructure/
│   ├── database/
│   ├── ssh/
│   └── llm/ollama/
├── composition/
└── domain/evaluation/
```

## Responsibility and dependency rules

- `core` owns provider-neutral contracts, configuration, exceptions, utilities, and fail-closed diagnostic policy. It does not import interfaces, infrastructure, composition, capabilities, or Claude runtime.
- `capabilities` owns bounded monitoring, analysis/RAG, investigation/evidence, knowledge, and remediation behavior. It does not import interfaces.
- `runtime/claude` owns native Claude CLI process execution, stream decoding, runtime result interpretation, and `AgentJob` lifecycle. Claude decides workflow order; Python validates and executes every capability.
- `interfaces/mcp` owns the single MCP registry/protocol server and stable Claude-visible tool names. The `.mcp.json` entrypoint remains `tools/run_project_mcp_server.py`.
- `interfaces/admin` owns HTTP routes, schemas, Admin services, templates, and static assets. Agent Runs reads the existing `agent_jobs` projection; no duplicate observability model was added.
- `infrastructure/database` owns SQLAlchemy engine/session/models/repositories. `infrastructure/ssh` is the only package importing `asyncssh`; known-hosts checking, key validation, connection timeout, command timeout, and result semantics remain enforced there.
- `infrastructure/llm/ollama` owns Ollama-specific clients. Ollama is the only configured provider.
- `composition` wires the application. It does not implement workflows.
- `app/shared` has been eliminated; contracts, configuration, exceptions, utilities, and application services now have canonical owners.

## Safety boundaries

Claude receives only MCP tools with bounded permissions. It has no raw SQL, raw SSH, unrestricted shell, direct database, direct Ollama, or remediation-bypass capability. MCP handlers call Python capabilities; policy, evidence, persistence, and approval remain Python-owned. `No solution found` remains a valid remediation result.

## Compatibility facades

Thin facades remain at historical import paths required by existing tests and callers:

- `app/domain/{analysis,investigation,knowledge}` → `app/capabilities` and `app/core`.
- `app/tools` has been eliminated; MCP catalog and boundary code live under `app/interfaces/mcp`, monitoring and SSH live under their canonical capability/infrastructure packages.
- `app/admin` and `app/mcp` → `app/interfaces/admin` and `app/interfaces/mcp`.
- No `app/shared` compatibility layer remains; database, contracts, configuration, and application services have canonical owners.

These facades contain no duplicate business implementation. `app/domain/evaluation` remains a single evaluation/readiness implementation rather than a migrated duplicate.

## Verification

- Normal suite: `407 passed, 1 skipped`.
- Real Claude/Ollama/MCP acceptance: accepted against operational server 2 using native `claude`, Ollama model `gemma4:e4b-it-q4_K_M`, connected `vps` MCP, persisted `AgentJob`, report, analysis, investigation, and observability.
- The acceptance also exposed and fixed bounded persistence of oversized `agent_jobs.error_message` values without changing the schema.
