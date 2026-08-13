# C.14.10 Claude runtime observability

C.14.10 adds a read-only observability projection over the existing
`agent_jobs` persistence model.

No second telemetry database and no schema migration are introduced.

## Trace fields

Each persisted Claude job is normalized into a trace containing:

- job, server, session and lifecycle timestamps;
- runtime duration and API duration;
- turns and tool-call counts;
- ordered MCP/tool-use names;
- mandatory monitoring/analysis tool verification;
- MCP server connection status;
- Specialist delegation count;
- investigation and remediation progression flags;
- stop reason, subtype and error state;
- input/output token usage and model usage;
- runtime/provider/agent metadata;
- persisted error code and message.

## Admin API

- `GET /api/agent-observability/jobs`
- `GET /api/agent-observability/jobs/{job_id}`
- `GET /api/agent-observability/summary`

The summary reports recent success/failure counts, success rate, average
duration, average tool calls, Specialist delegations, MCP disconnects,
mandatory-tool verification failures, and top tool calls.

This is an observability/read concern only. Claude remains the workflow
orchestrator and Python remains the bounded execution and policy layer.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
