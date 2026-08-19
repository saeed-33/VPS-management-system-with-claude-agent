# Current Test Results

<!-- DOC-STATUS: CURRENT_CANONICAL -->

Run date: **2026-08-14**  
Environment: isolated project environment outside the repository; WSL remains
the documented stable environment
Python: **3.14.3**
pytest: **8.4.2**  
Warning: one existing Starlette/httpx deprecation warning.

## Regression

Exact command:

```bash
uv run --no-sync python -m pytest -q -o addopts="" --ignore=tests/acceptance/external_runtime
```

Result: **620 passed, 0 failed, 0 skipped, 1 warning**. The equivalent full
collection reports four opt-in real-runtime skips.

The command was not run with live real-runtime tests. No live SSH or
destructive remediation was executed for documentation.

## Current project checks

| Check | Result |
|---|---|
| Route inventory | 99 total; 73 OpenAPI; 26 web-only |
| PostgreSQL schema | 33/33 tables; pgvector OK; 3/3 custom RAG indexes; schema PASS |
| MCP catalog | 25 tools |
| `python -m compileall -q app tests` | PASS |
| `git diff --check` | PASS |
| Admin UI/RBAC regression | PASS within full suite; focused UI/auth tests passed |
| Phase 5/6/7 deterministic regression | PASS within full suite |

## Live evidence status

The normal run excludes `tests/real_runtime`. Phase 5 real acceptance is
recorded as passed. Phase 6 live status remains contradictory between the JSON
artifact and final report. Phase 7 real acceptance is recorded as PASS in
`docs/final-acceptance/`; Specialist final E2E remains partial with an accepted
non-blocking limitation. These are acceptance dispositions, not claims of
runtime failure.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: real acceptance PASS; Specialist final E2E partial and accepted
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
