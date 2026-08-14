# Data and Database Architecture

The authoritative schema check is `tools/bootstrap_database.py --verify-only`.
The current PostgreSQL database verifies 33/33 expected tables, pgvector, and
3/3 custom RAG indexes. SQLAlchemy models are registered in
`app/infrastructure/database/models/__init__.py`.

## Domain groups

| Group | Tables |
|---|---|
| Monitoring | `servers`, `monitor_commands`, `monitoring_profiles`, `monitoring_profile_commands`, `monitoring_reports`, `command_executions` |
| Analysis/RAG | `report_analyses`, `report_analysis_sources`, `report_retrieval_documents`, `knowledge_sources`, `knowledge_documents`, `knowledge_chunks` |
| Investigation | `investigations`, `investigation_specialist_candidates`, `specialist_definitions`, `agent_jobs` |
| Supervised remediation | `remediation_plans`, `remediation_sandbox_results`, `remediation_approvals`, `remediation_executions`, `remediation_verifications`, `remediation_rollbacks`, `remediation_evidence`, `remediation_audit_events`, `sandbox_validations` |
| Autonomous remediation | `autonomous_remediation_policies`, `autonomous_policy_decisions`, `autonomous_authorizations`, `autonomous_policy_execution_reservations`, `autonomous_policy_runtime_state`, `autonomous_policy_audit_events` |
| Admin security | `admin_users`, `admin_sessions`, `admin_auth_audit_events` |

Important relationships include reports to servers/profiles, analyses to
reports, investigations to servers/reports and Specialist candidates,
remediation plans to investigations/servers, approvals/executions/verification/
rollback/Evidence/audit to plans, and autonomous decisions/authorizations/
reservations/runtime/audit to policies and immutable plan fingerprints.

Safety indexes include unique policy IDs, decision IDs, authorization IDs and
tokens, unique reservation idempotency keys, reservation expiry/owner indexes,
policy match indexes, plan-created indexes, and Admin session/audit expiry/user
indexes. RAG uses GIN full-text, scope, and HNSW cosine indexes.

Migrations are additive SQL files under
`app/infrastructure/database/migrations/`, including the Phase 5 remediation,
Phase 6 sandbox, Phase 7 autonomous, and Admin authentication boundaries.
No new migration was introduced for the documentation task.

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
