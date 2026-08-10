# Investigation Administration UI — Phase 4.19.4

Phase 4.19.4 adds read-only Administration UI pages backed by the Phase 4.19.3 API.

Pages:

```text
GET /investigations
GET /investigations/{investigation_id}
```

The list page shows status, server/report references, selected Specialists, runtime availability, and Final Diagnosis availability.

The detail page may show persisted runtime data:

```text
Specialist runs
Evidence
Correlated claims
Conflicts
Deterministic Final Diagnosis
LLM narrative and fallback state
```

The UI is read-only and does not execute Specialists, SSH, tools, correlation, or LLM synthesis.

Next: Phase 4.19.5 — Web/API Acceptance.
