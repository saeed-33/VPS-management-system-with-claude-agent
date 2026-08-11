# Database Bootstrap

## الهدف

`tools/bootstrap_database.py` هو المصدر التشغيلي لإنشاء قاعدة **جديدة** مطابقة للنماذج الحالية، بدل مطالبة المطور بإعادة تطبيق سلسلة migrations التاريخية يدويًا على قاعدة فارغة.

## لماذا لا يكفي startup؟

التطبيق يستدعي `Base.metadata.create_all()` عند startup، وهذا ينشئ الجداول المسجلة في SQLAlchemy metadata، لكنه لا:

- ينشئ PostgreSQL database.
- يثبت pgvector extension.
- يضمن الفهارس المخصصة التي أضيفت تاريخيًا عبر SQL migrations.

لذلك bootstrap ينفذ كل ما يلزم قبل تشغيل التطبيق.

## الجداول المتوقعة

```text
servers
monitor_commands
monitoring_profiles
monitoring_profile_commands
monitoring_reports
command_executions
report_analyses
report_analysis_sources
report_retrieval_documents
```

هذه القائمة مأخوذة من `app.shared.database.models`.

## الفهارس الخاصة بالـRAG

بالإضافة إلى الفهارس التي ينشئها SQLAlchemy من `index=True` وunique constraints:

```text
ix_retrieval_search_vector_gin
ix_retrieval_scope
ix_retrieval_embedding_hnsw_cosine
```

## تنفيذ

```powershell
uv run python tools/bootstrap_database.py
```

## صلاحيات PostgreSQL

قد تحتاج:

- `CREATEDB` لإنشاء `POSTGRES_DB`.
- صلاحية `CREATE EXTENSION vector` داخل قاعدة الهدف.

في الإنتاج يفضل أن ينشئ DBA القاعدة والامتداد ثم يشغل مستخدم التطبيق:

```powershell
uv run python tools/bootstrap_database.py --skip-create-database
```

## عدم إسقاط البيانات

السكربت **لا ينفذ DROP DATABASE ولا DROP TABLE**، ولا يحذف بيانات. هو idempotent بقدر الإمكان باستخدام create-if-missing وSQLAlchemy `create_all`.

## قواعد التطوير المستقبلي

عند إضافة model/table/index جديد:

1. أضف migration لترقية القواعد القائمة.
2. حدّث model.
3. إذا كان index/extension غير ممثل في SQLAlchemy metadata، حدّث bootstrap.
4. حدّث verification داخل bootstrap.
5. حدّث `docs/architecture/database.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
