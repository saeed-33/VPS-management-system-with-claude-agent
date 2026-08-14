# System Overview

The system monitors configured Linux VPS servers through verified SSH, stores
structured reports in PostgreSQL, analyses reports with deterministic reuse and
Ollama-backed analysis, and starts bounded investigations when the analysis
requires them. Results are persisted as Evidence and diagnoses. Remediation is
registered, fingerprinted, sandbox-validated, approval-controlled, verified,
and auditable.

```text
Admin / operator
       | authenticated Web/API + CSRF + RBAC
       v
FastAPI Admin interface ------------------------------+
       |                                               |
       v                                               v
PostgreSQL repositories <--- Python capabilities ---> SSH named commands
       ^                       |                       |
       |                       +--> Ollama adapters    |
       |                       +--> native Sandbox    |
       |                       +--> Evidence/audit    |
       |                                               |
Claude Code supervisory runtime --> bounded vps MCP --+
```

## Layer responsibilities

| Layer | Actual paths | Responsibility |
|---|---|---|
| Core | `app/core/` | Settings, contracts, fingerprints, risk/policy evaluators, safety rules. |
| Capabilities | `app/capabilities/` | Monitoring, reports, analysis, RAG, investigations, Specialists, remediation. |
| Claude runtime | `app/runtime/claude/` | Claude process/session contract, Ollama-backed runtime, jobs, parsing, observability. |
| Admin interface | `app/interfaces/admin/` | FastAPI endpoints, Jinja2 UI, vanilla JS, sessions, RBAC, CSRF, audit. |
| MCP interface | `app/interfaces/mcp/` | 25-tool catalog, schemas, handlers, protocol server, bounded serialization. |
| Database | `app/infrastructure/database/` | SQLAlchemy engine/models, PostgreSQL repositories, migrations, bootstrap. |
| SSH | `app/infrastructure/ssh/` | known-hosts client and bounded command executor. |
| Ollama | `app/infrastructure/llm/ollama/` | analysis, diagnosis, Specialist reasoning, and embeddings. |
| Composition | `app/composition/` | Repository/service/runtime wiring and application container. |

Dependencies point inward toward contracts and policies. Interfaces call
capabilities; capabilities call repositories and infrastructure through
composition. Claude and MCP do not become an alternate execution layer.

## Implemented boundaries

- Monitoring reads CPU, memory, storage, services, logs, and configured
  commands, then persists reports and command executions.
- Analysis supports exact reuse, structured compatibility, full-text/vector
  retrieval, and Ollama analysis.
- Investigations route to DB-defined Specialists, whose loop evaluates policy,
  executes registered read-only tools, collects Evidence, and persists results.
- Remediation reuses the named write registry and existing Evidence rather than
  rebuilding Evidence collection.
- Autonomous remediation is a deterministic overlay and is disabled globally
  by default.

Phase 6/7 live acceptance is not called closed in this document until the
repository's conflicting evidence is reconciled; deterministic implementation
coverage remains documented as implemented.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
