# C.14.11A.4.2c — Analysis and Investigation Composition

This step extracts RAG, analysis, and LLM-backed investigation construction
from `app/composition/builder.py` into `app/composition/analysis.py`.

The extraction preserves the previous composition order:

1. repositories and deterministic core services
2. retrieval/RAG/PDF composition
3. admin SSH service
4. LLM analysis + specialist investigation composition
5. monitoring, MCP, Claude runtime, and scheduler wiring

The remaining runtime wiring is intentionally left in `builder.py` for A.4.2d.

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
