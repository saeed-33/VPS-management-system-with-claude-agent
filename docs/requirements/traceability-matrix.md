# Requirements Traceability Matrix

The matrix is intentionally concise; each row points to the stable
requirement, use-case family, implementation, test/evidence, and status.

| Specification | FR/NFR | Use case | Component | Test/evidence | Status |
|---|---|---|---|---|---|
| 1 | FR-001..003, NFR-DATA-001 | UC-001..003 | monitoring services, SSH, reports, PostgreSQL | monitoring/report tests; schema verify | IMPLEMENTED |
| 2-4 | FR-004..008 | UC-004..008 | analysis, Ollama, RAG, diagnosis | analysis/RAG/grounding tests; C.14.12 artifact | IMPLEMENTED |
| 5 | FR-010, NFR-SEC-005 | UC-010 | sandbox runtime and validation | Phase 6 deterministic tests; conflicting live record | PARTIAL |
| 6 | FR-012, FR-015..018 | UC-012, UC-017..020 | remediation/autonomous services | policy, circuit, authorization, concurrency tests | PARTIAL |
| 7 | FR-022 | UC-008 | diagnosis/Evidence contracts | grounding tests; no dedicated source locator | PARTIAL |
| 8 | FR-023 | UC-021 | future notification adapter | no current implementation | DEFERRED |
| 9 | FR-011..012, NFR-SEC-001..002 | UC-011..015, UC-024..026 | Admin auth/RBAC/remediation | Admin auth/API/UI/Phase 5 tests | IMPLEMENTED |
| Safe boundary | NFR-SEC-003..006 | UC-017..020 | core policies, MCP, authorization/reservation | negative security and recovery tests | IMPLEMENTED |
| Persistence | NFR-DATA-001..002 | all | database/bootstrap/MCP | 33/33, 25 tools | IMPLEMENTED |
| Audit | NFR-AUD-001..002 | UC-020, UC-023..026 | audit repositories/Admin Audit | audit/security tests | IMPLEMENTED |
| Live proof | NFR-OPS-001 | UC-010, UC-017 | real acceptance harness | evidence conflict/absence | DEFERRED |

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
