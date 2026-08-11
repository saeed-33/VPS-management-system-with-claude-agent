# Specialist Investigation Skill

Use this skill when initial analysis identifies potential issues that require
deeper investigation.

## Boundaries

Specialist definitions are database-managed. Claude agent files provide generic
roles only and are not the source of truth.

## Required workflow

```text
read analysis
get available Specialists from project services
select Specialists within registry/budget constraints
run Specialist tasks through project services
collect Evidence and results
aggregate per-server findings
read or produce final diagnosis through project services
```

Specialist reasoning must use project Ollama clients when operational tools are
available.
