# Production Deployment Baseline

هذه الوثيقة تصف طريقة نشر آمنة نسبيًا **للبنية الحالية** قبل إضافة نظام الوكلاء المتخصصين.

## الحالة الحالية

التطبيق هو FastAPI process واحد يحتوي داخله على:

- HTTP API / Admin UI.
- MonitoringScheduler.
- AnalysisAgentManager وqueues.
- RAG/LLM orchestration.
- PostgreSQL repositories.

```text
Reverse Proxy / Private Network
            |
         FastAPI
            |
   +--------+---------+
   |                  |
Scheduler       Analysis queues
   |                  |
  SSH            LLM / RAG
   |                  |
Servers            PostgreSQL
```

## قيد مهم: Worker واحد فقط

لا تستخدم حاليًا:

```text
uvicorn ... --workers 4
gunicorn multiple workers
```

كل process جديد يشغل `MonitoringScheduler` أثناء FastAPI lifespan، والـanalysis queues process-local. تعدد workers قد يكرر monitoring jobs ويقسم queues بشكل غير منسق.

Baseline الحالي:

```powershell
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

إذا احتجنا horizontal scaling لاحقًا يجب فصل Scheduler/Workers أو إضافة distributed locking/leader election وqueue مشتركة.

## Topology موصى بها حاليًا

```text
Internet / Admin network
        |
 Firewall / VPN
        |
 Reverse Proxy + TLS + Auth
        |
 127.0.0.1:8000
        |
 chat_system (single process)
        |
 PostgreSQL / Ollama
```

الأفضل عدم جعل Uvicorn نفسه Internet-facing.

## Uvicorn

Development:

```powershell
uv run python -m uvicorn app.main:app --reload
```

Production-like:

```powershell
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

لا تستخدم `--reload` في الإنتاج.

## Startup sequence

FastAPI lifespan الحالي:

1. ينفذ `create_database_tables()`.
2. يستعيد pending analysis jobs إن كان AnalysisAgentManager مفعلًا.
3. يبدأ MonitoringScheduler.

عند shutdown:

1. يوقف scheduler.
2. يلغي scheduler task.
3. يعمل drain للـanalysis queues قدر الإمكان.

لذلك يجب أن يسمح process manager بـgraceful shutdown بدل kill فوري.

## Database

قبل أول تشغيل:

```powershell
uv run python tools/bootstrap_database.py
```

أو verification فقط:

```powershell
uv run python tools/bootstrap_database.py --verify-only
```

في الإنتاج يفضل:

- PostgreSQL role مخصص للتطبيق.
- عدم استخدام superuser للتشغيل اليومي.
- backup policy.
- اختبار restore فعلي.
- تقييد PostgreSQL network exposure.

## LLM / Embeddings

إذا كان Ollama محليًا، يفضل أن يكون غير مكشوف للعامة.

يجب توفر:

```text
Analysis model:  qwen3:8b (default)
Embedding model: nomic-embed-text
```

إذا كان `LLM_PROVIDER=openai` يجب حماية `OPENAI_API_KEY` كسر وليس داخل Git.

## SSH

يفضل:

- مستخدم SSH محدود الصلاحيات.
- مفتاح منفصل للمراقبة.
- عدم استخدام root ما لم يكن ضروريًا.
- `known_hosts` فعلي وعدم تعطيل host verification.
- أوامر monitoring read-only قدر الإمكان.
- حماية private key permissions على نظام التشغيل.

## Logs

التطبيق الحالي يستخدم Python `logging.basicConfig` إلى stdout/stderr بصيغة زمن/مستوى/logger/message.

في الإنتاج اجعل systemd/Docker/collector مسؤولًا عن:

- rotation.
- retention.
- central collection.
- access control.
- disk usage limits.

## Deployment change procedure

قبل deploy:

```powershell
git status
uv sync
uv run python -m pytest
uv run python tools/bootstrap_database.py --verify-only
uv run python tools/list_routes.py
```

ثم:

1. backup database عند وجود migration.
2. تطبيق migration المطلوبة.
3. restart process واحد.
4. فحص `/health`.
5. فحص Dashboard.
6. مراقبة أول monitoring cycle.
7. التحقق من وصول analysis إن كان LLM مفعلًا.
8. مراجعة logs للأخطاء.

## Rollback

الكود يمكن rollback إلى commit سابق، لكن database rollback ليس تلقائيًا.

قبل migration غير backward-compatible يجب تحديد:

- backup.
- rollback SQL أو restore strategy.
- توافق النسخة السابقة مع schema الجديدة.

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution see `docs/testing/TESTING_STRATEGY.md`.

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
