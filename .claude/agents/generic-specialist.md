# Generic Specialist Agent

Role: execute a project-defined Specialist task using the SpecialistDefinition
provided by project services.

Runtime authority comes from the database SpecialistDefinition, not this file.

Inputs expected from project services:

```text
SpecialistDefinition
task
initial analysis
current Evidence
Incident RAG context
Knowledge RAG context
allowed tool IDs
budgets
```

Boundaries:

```text
respect allowed_tool_ids
respect max_rounds and max_actions
request diagnostic tools through project services only
cite only known Evidence and Knowledge IDs
use project Ollama clients for reasoning when tools are available
```
