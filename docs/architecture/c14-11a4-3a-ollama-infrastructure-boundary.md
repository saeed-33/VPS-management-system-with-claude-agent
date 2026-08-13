# C.14.11A.4.3a — Ollama Infrastructure Boundary

> Historical migration record. C.14.11A structural closure removed the
> temporary compatibility modules mentioned by this migration.

Provider-specific Ollama implementations live under:

- `app/infrastructure/llm/ollama/analysis_client.py`
- `app/infrastructure/llm/ollama/embedding_client.py`

Provider-neutral contracts live in `app/core` and capability-owned modules.
The historical Ollama facades are no longer present.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
