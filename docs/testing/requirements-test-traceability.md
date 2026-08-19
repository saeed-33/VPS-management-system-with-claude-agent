# Requirements-to-Test Traceability

| Requirement area | Primary tests |
|---|---|
| Monitoring/report/analysis | `test_*monitoring*`, `test_*report*`, `test_*analysis*`, `test_hybrid_retriever.py` |
| Investigation/Specialists/Evidence | `test_investigation_*`, `test_specialist_*`, `test_evidence_collection.py` |
| Supervised remediation | `tests/unit/capabilities/remediation/`, `tests/acceptance/readiness/test_supervised_remediation_*` |
| Autonomous policy | `tests/unit/core/policies/test_autonomous_remediation_policy.py`, `tests/acceptance/readiness/test_autonomous_negative_security.py`, `tests/acceptance/readiness/test_autonomous_circuit_breaker.py` |
| Authorization/replay/recovery | `tests/unit/capabilities/remediation/test_autonomous_authorization.py`, `tests/unit/capabilities/remediation/test_autonomous_execution_idempotency.py`, `tests/acceptance/readiness/test_autonomous_concurrency_recovery.py` |
| Claude/MCP boundary | `tests/integration/mcp/`, `tests/unit/runtime/claude/`, `tests/architecture/runtime/` |
| Admin/RBAC/UI | `tests/integration/admin/` |
| Schema/routes/static | `tests/integration/admin/test_route_inventory.py`, `tests/integration/mcp/test_tool_catalog.py`, `tests/architecture/infrastructure/`, bootstrap verify |

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
