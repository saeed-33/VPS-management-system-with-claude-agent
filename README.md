# AI VPS Management

نظام لمراقبة خوادم Linux عبر SSH وتحليل تقاريرها باستخدام LLM وRAG.

## الوضع الحالي
المشروع في نهاية المرحلة 3 ويدعم: monitoring profiles، SSH monitoring، exact fingerprint reuse، pgvector، PostgreSQL FTS، Hybrid Retrieval/RRF، Structured Compatibility، source tracing وperformance profiling.

> الوكلاء التشخيصيون المتخصصون والتنفيذ الذاتي وKnowledge RAG ليست منفذة بعد؛ موثقة فقط في roadmap.

## سير العمل
```text
Scheduler -> MonitoringService -> SSH -> Report
 -> AnalysisAgentManager -> AnalysisOrchestrator
      -> exact fingerprint -> REUSE
      -> Hybrid Retrieval -> ASSISTED -> LLM
      -> no accepted context -> FULL -> LLM
```

ابدأ من `docs/README.md`.

## الاختبارات
```powershell
uv run python -m pytest
uv run python tools/evaluate_rag.py
uv run python tools/report_rag_performance.py
```
Baseline الموثق: `20 passed`.
