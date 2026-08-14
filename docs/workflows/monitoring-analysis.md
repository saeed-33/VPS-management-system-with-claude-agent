# Monitoring and Analysis Workflow

```text
scheduler/manual trigger
  -> load server/profile/registered commands
  -> execute bounded SSH commands
  -> normalize measurements and logs
  -> persist report + command executions
  -> exact reuse / structured compatibility / hybrid retrieval
  -> Ollama analysis when reuse is insufficient
  -> persist analysis, claims, severity, and Evidence references
```

A healthy result ends without an investigation. A failure, provider timeout,
or malformed result is persisted as a controlled failure; it does not trigger
an unrestricted command path.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
