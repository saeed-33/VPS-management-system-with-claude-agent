# Running the Project

هذا الدليل يصف تشغيل المشروع الحالي من clone جديد حتى واجهة FastAPI.

## 1. المتطلبات

- Python `>= 3.14`.
- `uv`.
- PostgreSQL.
- امتداد PostgreSQL `pgvector` متاح على السيرفر.
- SSH private key و`known_hosts` صالحان للخوادم التي ستراقبها.
- Ollama إذا استخدمت LLM/Embeddings المحلية.
- بديلًا عن Ollama للتحليل فقط يمكن استخدام OpenAI حسب الإعدادات الحالية، بينما embedding provider الحالي هو Ollama.

## 2. جلب المشروع

```powershell
git clone https://github.com/saeed-33/chat_system.git
cd chat_system
```

## 3. تثبيت الاعتماديات

المشروع معرف في `pyproject.toml` ويستخدم Python 3.14+.

```powershell
uv sync
```

أو إذا كانت البيئة منشأة مسبقًا:

```powershell
uv run python --version
```

## 4. إنشاء ملف البيئة

انسخ:

```powershell
Copy-Item .env.example .env
```

ثم عدل القيم، خصوصًا:

- PostgreSQL credentials.
- مسارات SSH key وknown_hosts.
- `LLM_ENABLED`.
- Ollama/OpenAI settings.
- RAG settings عند الحاجة.

## 5. Ollama

إذا كان:

```env
LLM_PROVIDER=ollama
```

يجب تشغيل Ollama وتوفر نموذج التحليل، افتراضيًا:

```text
qwen3:8b
```

ولأن embedding provider الحالي هو Ollama يجب أيضًا توفر:

```text
nomic-embed-text
```

مثال:

```powershell
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

## 6. إنشاء قاعدة البيانات من الصفر

الأمر الموصى به:

```powershell
uv run python tools/bootstrap_database.py
```

السكربت:

1. يتصل بقاعدة الصيانة `postgres`.
2. ينشئ `POSTGRES_DB` إن لم تكن موجودة.
3. ينفذ `CREATE EXTENSION IF NOT EXISTS vector`.
4. يستورد جميع SQLAlchemy models.
5. ينفذ `Base.metadata.create_all()`.
6. ينشئ فهارس RAG الخاصة:
   - `ix_retrieval_search_vector_gin`
   - `ix_retrieval_scope`
   - `ix_retrieval_embedding_hnsw_cosine`
7. ينفذ `ANALYZE`.
8. يتحقق من الجداول والامتداد والفهارس و`search_vector` و`vector(768)`.

إذا كانت قاعدة البيانات منشأة بواسطة administrator ولا يملك مستخدم التطبيق `CREATEDB`:

```powershell
uv run python tools/bootstrap_database.py --skip-create-database
```

للتحقق فقط:

```powershell
uv run python tools/bootstrap_database.py --verify-only
```

### قاعدة جديدة مقابل قاعدة قائمة

`bootstrap_database.py` هو **Bootstrap للحالة الحالية** ومناسب لبيئة جديدة.

لقاعدة إنتاج قائمة، لا تستخدمه كبديل عن تاريخ migrations عند تغيير schema. migrations التاريخية تبقى في:

```text
app/shared/database/migrations/
```

خصوصًا عند تغييرات قد تتطلب backfill أو تحويل بيانات.

## 7. اختبار المشروع

```powershell
uv run python -m pytest
```

ثم اختياريًا:

```powershell
uv run python tools/evaluate_rag.py
uv run python tools/report_rag_performance.py
```

## 8. تشغيل التطبيق

للتطوير:

```powershell
uv run python -m uvicorn app.main:app --reload
```

أو بدون reload:

```powershell
uv run python -m uvicorn app.main:app
```

افتراضيًا:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
GET /health
```

## 9. ماذا يحدث عند startup؟

`app.main` يقوم خلال lifespan بـ:

1. `create_database_tables()` لإنشاء الجداول الناقصة المسجلة في SQLAlchemy metadata.
2. استعادة jobs غير المكتملة إذا كان تحليل LLM مفعلًا.
3. تشغيل `MonitoringScheduler`.

> ملاحظة: `create_database_tables()` لا ينشئ قاعدة PostgreSQL نفسها، ولا يثبت pgvector، ولا يضمن فهارس HNSW/GIN المخصصة. لهذا يوجد `tools/bootstrap_database.py`.

## 10. أول إعداد وظيفي

بعد التشغيل، استخدم واجهة الإدارة/API لإنشاء:

1. Monitoring Commands.
2. Monitoring Profile.
3. ربط الأوامر بالـProfile وترتيبها.
4. Server مع SSH settings.
5. ربط Server بالـMonitoring Profile.
6. تفعيل monitoring.

بعدها يبدأ scheduler بجمع التقارير، وإذا `LLM_ENABLED=true` ترسل التقارير إلى analysis queue.

## 11. الإيقاف

`Ctrl+C`.

أثناء shutdown:

- scheduler يتوقف.
- scheduler task تلغى.
- AnalysisAgentManager يحاول drain للـqueues قبل الإغلاق.
