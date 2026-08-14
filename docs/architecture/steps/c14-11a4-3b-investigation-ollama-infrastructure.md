# C.14.11A.4.3b — Investigation Ollama Infrastructure

Moved Ollama-specific investigation adapters into
`app/infrastructure/llm/ollama/`:

- `OllamaSpecialistReasoningClient`
- `OllamaFinalDiagnosisNarrativeClient`

Provider-neutral contracts and factories remain in their historical
investigation modules for now.

Factories import the Infrastructure adapters lazily when called, avoiding an
import-time circular dependency. Historical class names remain available via
module-level `__getattr__` compatibility shims until A.4.6.

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
