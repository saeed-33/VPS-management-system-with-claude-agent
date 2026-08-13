# Autonomous Remediation API

The Admin API is under `/api/autonomous-remediation` and is operator-facing.
It provides policy CRUD and explicit enable/disable/suspend/resume actions,
read-only candidate discovery, decision history, execution reservations,
runtime state, and historical outcome queries.

The project MCP boundary exposes only two Phase 7 capabilities: the existing
bounded planning/sandbox/approval tools and `attempt_autonomous_remediation`.
The attempt input is only `{ "plan_id": "..." }`; policy fields,
authorization tokens, server IDs, shell text, and kill-switch values are not
MCP inputs.

The MCP call returns a structured denial or approval-required result when the
deterministic evaluator does not authorize execution. It cannot create or
modify a policy.
