# Current Architecture

## الصورة العامة
```text
Admin/Web
   |
Shared Services / Repositories
   |
MonitoringScheduler
   |
MonitoringService
   +--> SSHClient -> SSHCommandExecutor
   |
Monitoring Report
   |
AnalysisAgentManager
   |
AnalysisOrchestrator
   +--> ReportNormalizer
   +--> ReportFingerprintService
   +--> AnalysisReusePolicy
   +--> HybridRetriever
   |      +--> RagRetriever (pgvector)
   |      +--> FullTextRetriever (PostgreSQL FTS)
   |      +--> RRF
   |      +--> semantic threshold
   |      +--> StructuredCompatibilityChecker
   +--> RagContextBuilder
   +--> ReportAnalyzer / LLM
   +--> RetrievalIndexer
   |
PostgreSQL + pgvector
```

## المسؤوليات
- Monitoring يجمع الحالة ولا يشخصها.
- Analysis يحول التقرير إلى نتيجة تحليل.
- Retrieval يسترجع حالات تاريخية مساعدة.
- Reuse Policy يحدد REUSE/ASSISTED/FULL.
- Repositories تعزل SQL/SQLAlchemy.
- `app/bootstrap.py` هو composition root.

## invariants
1. Exact fingerprint فقط يسمح بـREUSE.
2. Semantic similarity تستخدم للسياق، لا لإعادة الاستخدام.
3. Full-Text وحده لا يدخل LLM context.
4. RRF ranking signal وليس similarity percentage.
5. Structured conflict يستطيع رفض candidate عالي similarity.
6. فشل RAG لا يمنع FULL analysis.
7. فشل analysis queue لا يفشل monitoring report.

## غير منفذ حاليًا
Specialist agents، autonomous diagnostics، Knowledge RAG للوثائق، وautomatic remediation.
