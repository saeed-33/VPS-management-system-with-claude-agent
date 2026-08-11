# Server Monitoring Skill

Use this skill when supervising periodic or operator-triggered monitoring for
one or more servers.

## Boundaries

Monitoring execution is owned by Python services. Do not use raw SSH, raw shell,
or prompt-authored command execution as the normal workflow.

## Required workflow

```text
load server context
load monitoring profile
run project monitoring
wait for completion
read persisted report
continue to analysis workflow
```

## Outputs

Return structured references to persisted reports and monitoring status. Do not
invent report IDs or command execution IDs.
