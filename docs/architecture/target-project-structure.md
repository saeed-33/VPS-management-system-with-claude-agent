# Target Project Structure

## Goal

The codebase should make Claude the supervisory runtime and keep Python modules
as tools, domain services, persistence, API, and UI.

## Recommended Structure

```text
app/
  runtime/
    claude/
      supervisor.py
      session.py
      runtime.py
      result_parser.py
      monitoring_cycle.py
      multi_specialist_supervision.py
      job_service.py
      models.py
      exceptions.py
  tools/
    monitoring/
    reports/
    retrieval/
    investigation/
    specialists/
    remediation/
    ssh/
  domain/
    analysis/
    investigation/
    knowledge/
    evaluation/
  shared/
    config.py
    dto/
    database/
    services/
    utils/
  mcp/
    schemas.py
    serializers.py
    project_tools.py
    server.py
  admin/
    api/
    services/
    web/
```

## Responsibilities

`app/runtime/claude/` contains the Claude runtime adapter, session execution,
job tracking, supervisor entrypoint, and Claude-facing workflow prompts.

`app/tools/` contains deterministic capabilities Claude can call. Tools validate
input, call domain services, and return structured outputs.

`app/domain/` contains business logic: analysis, retrieval, investigations,
specialist contracts, evaluation, and knowledge handling.

`app/shared/` contains configuration, DTOs, database models, repositories,
cross-cutting services, and utilities.

`app/mcp/` exposes project tools to Claude through stable schemas and
serializers. `app/mcp/server.py` is the stdio MCP protocol surface configured
from `.mcp.json`.

`app/admin/` remains the operator control plane for viewing state and approving
actions.

## Design Rules

Claude-native coordination should stay in Claude. Python should not reimplement
planning, delegation, or synthesis when Claude can perform those steps through
tools.

Tool outputs must be structured, auditable, and persisted when they affect
operator-visible state.

SSH, SQL, Ollama, and remediation execution must remain behind project tools and
policy checks.

Operator-facing views must read state through admin APIs and project services.
They should not encode supervisory workflow order or high-level branch
decisions.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
