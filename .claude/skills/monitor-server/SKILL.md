---
name: monitor-server
description: Monitor exactly one registered server through project MCP tools, validate its monitoring configuration, and return the persisted report reference for downstream analysis. Use for scheduled or operator-triggered per-server monitoring.
argument-hint: "<server_id>"
allowed-tools:
  - mcp__vps__get_server_context
  - mcp__vps__get_monitoring_profile
  - mcp__vps__run_monitoring
  - mcp__vps__get_latest_report
---

# Monitor Server

## Purpose

Run one bounded monitoring cycle for one persisted server using only project
capabilities. This skill does not execute SSH or shell commands directly.

## Input contract

Required input:

```text
server_id: positive integer
```

Do not accept or request server passwords, private keys, raw commands, or SQL.

## Preconditions

1. Call `mcp__vps__get_server_context` with `server_id`.
2. If the tool fails, stop and return the tool's controlled failure.
3. Require `server.monitor_enabled == true`.
4. Require a positive `server.monitoring_profile_id`.
5. Call `mcp__vps__get_monitoring_profile` with that profile id.
6. If the tool fails, stop.
7. Require `profile.enabled == true`.

Do not invent or replace a missing monitoring profile.

## Workflow

1. Read and validate server context.
2. Read and validate the assigned monitoring profile.
3. Call `mcp__vps__run_monitoring` exactly once for the server.
4. Require a successful tool result.
5. Require `persisted_report` in the monitoring result.
6. Call `mcp__vps__get_latest_report` for the same server.
7. Verify the latest persisted report represents the completed monitoring cycle.
   When both responses expose report IDs, they must match.
8. Return the persisted report reference for `analyze-incident`.

## Failure behavior

Return a controlled outcome; do not bypass the project boundary.

Use these semantic outcomes when applicable:

```text
server_context_failed
monitoring_disabled
monitoring_profile_missing
monitoring_profile_disabled
monitoring_failed
persisted_report_missing
persisted_report_mismatch
```

Do not automatically retry `run_monitoring` inside this skill. Retry policy
belongs to the bounded runtime/session layer so duplicate monitoring reports are
not silently created.

## Stopping conditions

Stop when:

```text
a precondition fails
run_monitoring fails
a persisted report cannot be verified
the persisted report has been verified successfully
```

## Output contract

Return a compact structured result with:

```text
status
server_id
monitoring_profile_id
report_id
generated_at, when present
error_code, when failed
error_message, when failed
```

Never invent a report ID or command execution ID.
