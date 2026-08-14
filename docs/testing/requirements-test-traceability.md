# Requirements-to-Test Traceability

| Requirement area | Primary tests |
|---|---|
| Monitoring/report/analysis | `test_*monitoring*`, `test_*report*`, `test_*analysis*`, `test_hybrid_retriever.py` |
| Investigation/Specialists/Evidence | `test_investigation_*`, `test_specialist_*`, `test_evidence_collection.py` |
| Supervised remediation | `test_phase5_*`, `test_phase6_*`, `test_phase5_admin_api.py` |
| Autonomous policy | `test_autonomous_remediation_policy.py`, `test_phase7_negative_security.py`, `test_phase7_circuit_breaker.py` |
| Authorization/replay/recovery | `test_autonomous_remediation_authorization.py`, `test_autonomous_execution_idempotency.py`, `test_phase7_concurrency_recovery.py` |
| Claude/MCP boundary | `test_project_mcp_*`, `test_claude_*`, `test_c14_9_*`, `test_c14_11a3_ollama_only_contract.py` |
| Admin/RBAC/UI | `test_admin_auth_rbac.py`, `test_admin_ui_completion.py`, `test_admin_system_*` |
| Schema/routes/static | `test_route_inventory.py`, `test_project_tool_catalog.py`, `test_c14_11a4_3d_*`, bootstrap verify |

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
