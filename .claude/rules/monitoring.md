# Monitoring Rule

Monitoring is project-owned execution.

Claude Code may supervise monitoring order and interpret project-tool results,
but must not replace `MonitoringScheduler`, `MonitoringService`, SSH command
execution, report persistence, or monitoring profile validation with prompt-only
logic.

Required order:

```text
periodic trigger
 -> per-server subordinate agent
 -> get server/profile context through project tools
 -> run project-owned monitoring
 -> wait for monitoring completion
 -> read persisted report
```

Operational monitoring tools are introduced in later Phase C steps. Until then,
this file is a boundary definition only.
