# Performance Baseline

الأداة:
```powershell
uv run python tools/dev/report_rag_performance.py
```

آخر عينة موثقة: 65 analyses.

## generated_with_context
تقريبًا:
```text
retrieval_total_ms   avg ~ 614 ms
embedding_ms         avg ~ 579 ms
vector_search_ms     avg ~   7 ms
full_text_search_ms  avg ~   3 ms
compatibility_ms     avg ~   7 ms
llm_ms               avg ~10.7 s
orchestrator_total   avg ~11.8 s
historical contexts      ~3
historical chars         ~4.8k
user prompt chars        ~15.7k
```

## reused
```text
orchestrator_total p50 ~31.5 ms
reuse_index_ms     p50 ~ 9.2 ms
```

بعد تحسين reuse، `index_reused_analysis()` ينسخ retrieval document/embedding عند توفر المصدر بدل embedding جديد.

## الاستنتاج
عنق الزجاجة في ASSISTED هو LLM، لا PostgreSQL vector/FTS أو compatibility. لا يوجد قرار حالي بضغط السياق قبل إثبات الحفاظ على جودة التحليل.

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution see `docs/testing/TESTING_STRATEGY.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

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
