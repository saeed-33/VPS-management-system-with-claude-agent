# C.14.11A.4.2a — Repository Composition

Repository construction is moved from `app/composition/builder.py` into
`app/composition/repositories.py`.

The new `RepositoryBundle` is composition-only. `build_container()` still
receives the same repository instances and downstream wiring is unchanged.

Next stages:
A.4.2b shared/domain services
A.4.2c analysis and investigation
A.4.2d Claude, MCP, and scheduler runtime

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
