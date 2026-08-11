# AI VPS Management

نظام لمراقبة خوادم Linux عبر SSH وتحليل تقاريرها باستخدام LLM وRAG، مع طبقة تحقيق تشخيصي متعددة الوكلاء ومقيدة بسياسات read-only.

## الوضع الحالي

المشروع أنهى التنفيذ والقبول حتى **Phase 4.17 — Dynamic Secondary Specialist Routing**.

```text
Phase 1–3                         completed
Phase 4.0–4.14                  completed
Phase 4.15 Server Coordinator    completed
Phase 4.16 LangGraph Parallel    completed
Phase 4.17 Dynamic Secondary     completed
Phase 4.18 Correlation/Diagnosis next
Phase 4.19 Investigation UI/API  planned
Phase 4.20 Evaluation/Safety     planned
```

آخر baseline اختبارات موثق بعد قبول 4.17:

```text
184 passed, 1 warning
```

الـwarning الحالي هو Starlette/TestClient deprecation warning وليس فشلًا وظيفيًا في Phase 4.17.

## القدرات المنفذة

### Monitoring + Initial Analysis

- monitoring profiles وSSH monitoring.
- report normalization وexact fingerprint reuse.
- PostgreSQL + pgvector وPostgreSQL Full-Text Search.
- Hybrid Retrieval باستخدام RRF وStructured Compatibility.
- Incident RAG مع source tracing وperformance profiling.

### Multi-Agent Investigation

- Dynamic user-defined Specialists وليس hard-coded agent classes.
- Specialist Registry وInvestigation Router وInvestigation persistence.
- Knowledge Sources وKnowledge RAG المنفصل عن Incident RAG.
- Specialist Context Builder وStructured Specialist Reasoning مع provenance validation.
- Diagnostic Tool Registry محدود بأدوات معروفة وread-only.
- Diagnostic Policy Engine قبل أي execution.
- Evidence Collection عبر SSH من approved execution envelopes فقط.
- Bounded Specialist Investigation Loop.
- Server Coordinator.
- LangGraph parallel Specialist execution.
- Dynamic secondary Specialist waves مع Registry/budget/duplicate validation.

## سير العمل الحالي

```text
Scheduler
  -> MonitoringService
  -> SSH
  -> Monitoring Report
  -> AnalysisOrchestrator
       -> exact fingerprint -> REUSE
       -> Incident Hybrid Retrieval -> ASSISTED/FULL analysis
  -> Investigation Router
  -> Dynamic Specialist selection
  -> Specialist Context
       + Current Evidence
       + Incident RAG
       + Knowledge RAG
  -> Specialist reasoning
  -> registered Tool request
  -> Diagnostic Policy
  -> approved read-only SSH Evidence
  -> bounded investigation loop
  -> LangGraph parallel wave
  -> optional validated secondary Specialist wave
```

## الحد الحالي

**Phase 4.18 — Correlation + Final Diagnosis** هي الخطوة التالية.

المطلوب فيها دمج عدة `SpecialistResult` وEvidence على مستوى السيرفر وإنتاج تشخيص يميز بين:

```text
confirmed
probable
unknown
```

مع traceability لكل claim مادي وإظهار التعارض بين نتائج Specialists بدل إخفائه.

لا توجد autonomous remediation في Phase 4.

## الاختبارات

```powershell
uv run python -m pytest
uv run python tools/evaluate_rag.py
uv run python tools/report_rag_performance.py
```

تفاصيل الـMulti-Agent والـruntime acceptance:

- `docs/testing/multi-agent-test-methodology.md`
- `docs/roadmap/phase-4-17-closeout.md`

ابدأ من `docs/README.md` لفهرس الوثائق الكامل.

## Phase 4 Production Readiness

Phase 4 autonomous diagnosis has completed the Phase 4.20 evaluation and safety gate.

Current operational state:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

Testing and architecture documentation:

- `docs/testing/TESTING_STRATEGY.md`
- `docs/testing/TEST_CATALOG.md`
- `docs/testing/RUNTIME_SCENARIOS.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/roadmap/phase-4-20-closeout.md`

Convenience commands:

```powershell
uv run python tools/run_all_tests.py --mode full
uv run python tools/run_all_tests.py --mode readiness --limit 500
uv run python tools/generate_test_catalog.py
uv run python tools/generate_project_structure.py
```
