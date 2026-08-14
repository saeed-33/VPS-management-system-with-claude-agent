# Real Acceptance Testing

Real acceptance is deliberately opt-in. The operator must first configure a
non-production target, exported environment values, PostgreSQL, Ollama,
Claude CLI, MCP, SSH known-hosts, and the native Sandbox where required.

Phase 5 acceptance proves supervised plan -> Sandbox -> approval -> named
write -> verification/rollback -> restoration. Phase 6 acceptance additionally
requires native WSL2 attestation. Phase 7 acceptance additionally requires
candidate eligibility, `AUTO_EXECUTE`, consumed authorization, successful
execution, verification, replay blocking, policy cleanup, and restored final
state.

The current repository does not contain a standalone Phase 7 result artifact.
Phase 6 has conflicting records: `artifacts/evaluation/phase6_readiness.json`
says `real_acceptance_status=PASS`, while
`docs/roadmap/phase-6-final-report.md` and the default opt-in test path say
`BLOCKED_BY_SANDBOX_RUNTIME`. This report records the contradiction instead of
selecting one without provenance.

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
