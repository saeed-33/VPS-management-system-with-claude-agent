# Measurable Non-Functional Requirements

Only values observed from current code/tests or directly verified commands are
reported as measured. Performance targets without a current benchmark are
marked `TARGET_DEFINED_BUT_NOT_MEASURED`.

| ID | Quality | Measurable statement and threshold | Method/evidence | Observed result | Status |
|---|---|---|---|---|---|
| NFR-SEC-001 | Access control | 100% of protected Admin Web/API routes require an authenticated session. | Auth middleware tests and route inventory | Pass | IMPLEMENTED |
| NFR-SEC-002 | CSRF | 100% of cookie-authenticated POST/PUT/PATCH/DELETE requests require a valid CSRF token. | `tests/test_admin_auth_rbac.py` | Pass | IMPLEMENTED |
| NFR-SEC-003 | Capability boundary | 0 unrestricted raw SSH, raw SQL, arbitrary shell, or unrestricted filesystem MCP capabilities. | MCP catalog/boundary and Claude least-privilege tests | Pass; catalog 25 | IMPLEMENTED |
| NFR-SEC-004 | Autonomous safety | Fresh configuration default `automatic_remediation_allowed` is false in 100% of loads. | `Settings` default and negative security tests | Pass | IMPLEMENTED |
| NFR-SEC-005 | Binding | 100% of autonomous executions require matching issue/plan/action/target/server/sandbox/Evidence bindings. | policy, authorization, idempotency, and negative tests | Pass in deterministic tests | IMPLEMENTED |
| NFR-SEC-006 | Replay | A consumed authorization permits 0 additional successful executions. | authorization replay tests | Pass | IMPLEMENTED |
| NFR-REL-001 | Idempotency | Concurrent attempts for one immutable autonomous idempotency binding have physical execution count <= 1. | concurrency/recovery tests | Pass in SQLite deterministic harness | IMPLEMENTED |
| NFR-REL-002 | Recovery | Expired reservation can be reclaimed only with the same immutable operation binding and owner token. | concurrency/recovery tests | Pass | IMPLEMENTED |
| NFR-REL-003 | Circuit breaker | A terminal failure is counted once and suspension requires explicit operator resume. | circuit-breaker tests | Pass | IMPLEMENTED |
| NFR-REL-004 | Rollback | Autonomous policy requires restoration capability; rollback failure blocks/suspends the path. | evaluator and circuit tests | Pass | IMPLEMENTED |
| NFR-DATA-001 | Persistence | Schema verification reports 33/33 expected tables, pgvector, and 3/3 custom indexes. | `tools/bootstrap_database.py --verify-only` on 2026-08-14 | Pass | IMPLEMENTED |
| NFR-DATA-002 | MCP stability | Catalog count is exactly 25 tools. | `ProjectMcpToolBoundary.list_tools()` | 25 | IMPLEMENTED |
| NFR-AUD-001 | Auditability | Admin auth, policy lifecycle, remediation, reservation, authorization, decision, execution, verification, rollback, and failure events are persisted or projected. | models/repositories/routes and tests | Pass in deterministic coverage | IMPLEMENTED |
| NFR-AUD-002 | Secret minimization | Admin read projections expose 0 session digests, passwords, authorization tokens, or reservation owner tokens. | Admin UI completion tests and serializers | Pass | IMPLEMENTED |
| NFR-PERF-001 | Latency | Bounded command timeout is 20 seconds and SSH connect timeout is 15 seconds; end-to-end p95 is <= a separately defined deployment target. | settings; no production p95 benchmark | timeout values measured; p95 not measured | TARGET_DEFINED_BUT_NOT_MEASURED |
| NFR-PERF-002 | Concurrency | `max_concurrent_servers` default is 5 and is configuration-bounded to 1-100. | `Settings` validation | 5 | IMPLEMENTED |
| NFR-MNT-001 | Regression | Current safe non-real suite has 0 failures. | stable WSL command on 2026-08-14 | 586 passed, 1 warning | IMPLEMENTED |
| NFR-MNT-002 | Static integrity | compileall and `git diff --check` both exit 0. | final validation | Pass | IMPLEMENTED |
| NFR-OPS-001 | Live readiness | Phase 6/7 live acceptance status has one consistent provenance record. | repository evidence review | Phase 6 conflict; Phase 7 absent | DEFERRED |

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
