# C.14.11A.4.2b — Container and Core Services

This step removes two responsibilities from the main composition builder:

1. `ApplicationContainer` moves to `app/composition/container.py`.
2. deterministic shared/domain service construction moves to
   `app/composition/services.py`.

The builder still owns analysis/investigation LLM composition and
Claude/MCP/scheduler runtime wiring. Those move in the next A.4.2 stages.

Behavior is preserved by aliasing every service bundle member back to the
same local variable names used by the existing builder.

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
