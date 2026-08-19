# Functional Requirements

Status values are based on current source/tests and do not convert a
deterministic test into live infrastructure acceptance.

| ID | Requirement | Component/surface | Evidence | Status |
|---|---|---|---|---|
| FR-001 | Register servers and monitoring commands/profiles. | `ServerService`, `ProfileService`, Admin API/UI | `tests/test_specialists_api.py`, route inventory, Admin UI tests | IMPLEMENTED |
| FR-002 | Collect CPU, memory, storage, services, and logs through bounded SSH commands. | `MonitoringService`, `SSHCommandExecutor` | monitoring and SSH boundary tests | IMPLEMENTED |
| FR-003 | Persist monitoring reports and command executions. | monitoring repositories/models | monitoring/report tests | IMPLEMENTED |
| FR-004 | Analyse reports using exact reuse, structured compatibility, retrieval, and Ollama. | `AnalysisOrchestrator`, RAG services | analysis/RAG tests; C.14.12 artifact | IMPLEMENTED |
| FR-005 | Classify issue severity and preserve structured claims/conflicts. | analysis contracts/policies | routing, conflict, safety tests | IMPLEMENTED |
| FR-006 | Route investigations to DB-defined Specialists with bounded budgets. | investigation router/registry/loop | Specialist and investigation tests | IMPLEMENTED |
| FR-007 | Collect and persist owned Evidence from Specialist execution. | `EvidenceCollectionService`, persistence | Evidence and Specialist persistence tests | IMPLEMENTED |
| FR-008 | Produce a grounded final diagnosis. | final diagnosis synthesizer | diagnosis grounding tests | IMPLEMENTED |
| FR-009 | Create immutable, fingerprinted remediation plans. | `RemediationService` | Phase 5/remediation tests | IMPLEMENTED |
| FR-010 | Validate a plan in the registered native sandbox before approval/execution. | Phase 6 sandbox runtime | sandbox tests; live status is unresolved | PARTIAL |
| FR-011 | Request, approve, or reject a persisted remediation plan. | remediation API/Admin UI | `tests/acceptance/readiness/test_supervised_remediation_admin_interface.py`, UI tests | IMPLEMENTED |
| FR-012 | Execute only registered approved actions and verify or rollback. | remediation execution/verification/rollback | Phase 5 tests and recorded acceptance report | IMPLEMENTED |
| FR-013 | Discover autonomous candidates from persisted history. | candidate/history services | autonomous policy/history tests | IMPLEMENTED |
| FR-014 | Create, update, enable, suspend, resume, and disable autonomous policies through Admin. | Admin policy API/UI | autonomous policy/RBAC/UI tests | IMPLEMENTED |
| FR-015 | Evaluate autonomous remediation as `AUTO_EXECUTE`, `REQUIRE_HUMAN_APPROVAL`, or `DENY`. | pure policy evaluator | policy/security/circuit tests | IMPLEMENTED |
| FR-016 | Require exact issue/plan/action/target/server/sandbox/Evidence bindings. | autonomous evaluator | negative security and idempotency tests | IMPLEMENTED |
| FR-017 | Issue and consume single-use authorization, reserve idempotently, execute outside transaction, and finalize with ownership. | autonomous execution/repository | authorization, concurrency/recovery tests | IMPLEMENTED |
| FR-018 | Suspend after configured failure threshold and require explicit operator resume. | circuit-breaker runtime | circuit-breaker tests | IMPLEMENTED |
| FR-019 | Expose safe autonomous reservations, authorizations, decisions, history, runtime, and audit projections. | Admin API/UI | Admin UI completion tests; route inventory | IMPLEMENTED |
| FR-020 | Authenticate Admin users with session cookies, RBAC, CSRF, expiry, and audit. | `AdminAuthService`, middleware | `tests/integration/admin/test_authentication_authorization.py` | IMPLEMENTED |
| FR-021 | Provide a bounded 25-tool MCP catalog to Claude. | MCP catalog/boundary | MCP catalog/boundary tests | IMPLEMENTED |
| FR-022 | Identify application-code failure locations without unsafe automatic code modification. | diagnosis/grounded narrative | no dedicated code-localization implementation found | PARTIAL |
| FR-023 | Send dangerous/sensitive proposals through social communication channels. | notification integration | no Telegram/social adapter in current source | DEFERRED |
| FR-024 | Keep automatic remediation disabled by default. | `Settings.automatic_remediation_allowed` | config and negative security tests | IMPLEMENTED |
| FR-025 | Record current live acceptance evidence for Phase 6 and Phase 7. | acceptance artifacts/docs | Phase 6 records conflict; Phase 7 record absent | DEFERRED |

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
