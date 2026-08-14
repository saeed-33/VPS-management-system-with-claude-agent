# C.14.11A.4.2d — Runtime Composition

Monitoring, MCP, Claude/Ollama runtime, and scheduler construction now live in
`app/composition/runtime.py`.

The main builder is reduced to composition coordination:

1. repositories
2. deterministic core services
3. retrieval/RAG/PDF
4. admin SSH test service
5. analysis/investigation
6. runtime composition
7. `ApplicationContainer`

The Claude-visible MCP contracts and tool names are unchanged. Claude continues
to decide WHAT/NEXT while Python remains responsible for policy enforcement and
safe execution.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
