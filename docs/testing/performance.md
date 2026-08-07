# Performance Baseline

الأداة:
```powershell
uv run python tools/report_rag_performance.py
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
