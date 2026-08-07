# Production Checklist

استخدم هذه القائمة قبل أي نشر production-like.

## Application

- [ ] `DEBUG=false`
- [ ] لا يوجد `--reload`
- [ ] Uvicorn worker واحد فقط في البنية الحالية
- [ ] `/health` يعمل
- [ ] الاختبارات تمر
- [ ] Route inventory تمت مراجعته

## Database

- [ ] PostgreSQL متاح
- [ ] pgvector extension موجود
- [ ] `bootstrap_database.py --verify-only` يعيد PASS
- [ ] GIN index موجود
- [ ] HNSW index موجود
- [ ] retrieval scope index موجود
- [ ] backup حديث
- [ ] restore procedure معروف
- [ ] DB user ليس superuser دون حاجة

## SSH

- [ ] private key موجود
- [ ] permissions مناسبة
- [ ] known_hosts موجود
- [ ] حساب SSH محدود
- [ ] أوامر المراقبة تمت مراجعتها
- [ ] SSH test يعمل لكل server

## LLM/RAG

- [ ] provider مضبوط
- [ ] analysis model متاح
- [ ] embedding model متاح
- [ ] RAG evaluation baseline معروف
- [ ] لا توجد current invariant failures

## Security

- [ ] التطبيق غير مكشوف للعامة بدون TLS/Auth
- [ ] secrets غير موجودة في Git
- [ ] `.env` غير منشور
- [ ] PostgreSQL غير مكشوف دون حاجة
- [ ] Ollama غير مكشوف للعامة
- [ ] access إلى Admin UI مقيد شبكيًا أو عبر proxy
- [ ] log retention محدد

## Deployment

- [ ] `git status` نظيف أو التغييرات معروفة
- [ ] migrations طبقت عند الحاجة
- [ ] process restart graceful
- [ ] أول monitoring cycle نجح
- [ ] analysis queue تعمل
- [ ] logs راجعت بعد deploy

## Rollback

- [ ] commit السابق معروف
- [ ] database rollback/restore plan موجود
- [ ] لا توجد migration غير قابلة للرجوع بدون backup
