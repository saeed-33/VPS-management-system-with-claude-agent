# Migrations and Troubleshooting

## Migrations
SQL migrations موجودة في `app/shared/database/migrations/`.
لا تعتبر تعديلات SQLAlchemy models بديلًا عن migration لقاعدة موجودة.

بعد migrations الخاصة بـRAG تحقق من:
- generated `search_vector` من نوع `tsvector`.
- GIN index للـFTS.
- scope index.
- HNSW index.
- pgvector extension/schema المناسب.

## pytest: No module named app
استخدم:
```powershell
uv run python -m pytest
```

## Similarity غير منطقية في UI
تأكد أن similarity تأتي من `vector_score` وليس `rrf_score`.

## Full-Text يعيد نتائج لكن لا تدخل ASSISTED
هذا قد يكون صحيحًا: Full-Text وحده لا يتجاوز semantic gate.

## High similarity candidate مرفوض
راجع Structured Compatibility؛ التعارض البنيوي يستطيع رفضه.

## RAG failure
السلوك المقصود هو الاستمرار إلى تحليل بدون historical context.

## REUSE performance
راقب `reuse_index_ms` و`orchestrator_total_ms`. المسار المحسن لا ينبغي أن يولد embedding جديدًا عندما يمكن نسخ retrieval document من المصدر.

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
