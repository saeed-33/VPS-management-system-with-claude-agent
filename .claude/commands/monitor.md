# monitor

Purpose: supervise one monitoring cycle through project-owned tools.

Required sequence:

```text
get server context
get monitoring profile
run project-owned monitoring
wait for completion
read persisted monitoring report
return structured cycle result
```

Do not use raw SSH or shell. In C.1 this command is documentation only; MCP
tools are added in later transition steps.
