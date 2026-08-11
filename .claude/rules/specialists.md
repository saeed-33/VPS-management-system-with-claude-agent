# Specialists Rule

Specialists are dynamic user-managed database records.

Do not create hard-coded domain Specialist files as the source of truth. Claude
agent files may define generic behavior only.

The authoritative Specialist definition comes from project services and
includes:

```text
slug
name
description
instructions
domains
trigger_hints
knowledge_topics
allowed_tool_ids
priority
max_rounds
max_actions
enabled status
```

Claude Code must respect enabled status, allowed tools, budgets, and project
policy. Specialist reasoning must route through the project Ollama clients when
operational tools exist.
