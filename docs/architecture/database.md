# Database Baseline

العلاقات المركزية:
```text
servers
  -> monitoring_reports
       -> report_analyses
            -> report_analysis_sources
            -> report_retrieval_documents
```

## report_analyses
الحقول الحرجة تشمل:
`report_id`, `server_id`, `status`, `health_status`, `summary`, `issues`,
`positive_findings`, `recommended_actions`, `report_fingerprint`,
`normalized_report`, `analysis_source`, `reused_from_analysis_id`,
`retrieval_strategy`, `retrieval_score`, `llm_called`, `performance_metrics`.

`report_id` فريد.

## report_retrieval_documents
يشمل:
`report_id`, `analysis_id`, `server_id`, `monitoring_profile_id`,
`command_set_hash`, `connection_successful`, `failed_command_ids`,
`error_signatures`, `fingerprint`, `normalized_text`, generated `search_vector`,
`structured_features`, `embedding`, embedding metadata و`analysis_health_status`.

`analysis_id` فريد. `embedding` حاليًا `Vector(768)`.

## الفهارس
Baseline يعتمد على GIN للـFTS، HNSW للـvector، وscope index يغطي
`server_id + monitoring_profile_id + command_set_hash`.

تغيير `EMBEDDING_DIMENSIONS` في البيئة لا يغير `Vector(768)` تلقائيًا؛ تغيير الأبعاد يحتاج migration وإعادة فهرسة.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
