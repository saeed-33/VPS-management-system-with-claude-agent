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

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
