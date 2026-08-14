# C.14.11A.4.2a — Repository Composition

Repository construction is moved from `app/composition/builder.py` into
`app/composition/repositories.py`.

The new `RepositoryBundle` is composition-only. `build_container()` still
receives the same repository instances and downstream wiring is unchanged.

Next stages:
A.4.2b shared/domain services
A.4.2c analysis and investigation
A.4.2d Claude, MCP, and scheduler runtime

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
