# Phase 4 Implementation Plan — Hierarchical Multi-Agent Investigation

**Status: Accepted implementation roadmap**

## Goal

تحويل النظام من تحليل تقرير منفرد إلى تحقيق هرمي متعدد الوكلاء لكل سيرفر، مع إبقاء التشخيص في Phase 4 ضمن حدود read-only وعدم إدخال remediation.

```text
Monitoring Report
      |
Initial Analysis
      |
Server Investigation
      |
Dynamic Specialist Selection
      |
Specialist Investigations
      |
Evidence + Incident RAG + Knowledge RAG
      |
Server-level Correlation
      |
Final Diagnosis
```

## Delivery rule

لا تعتبر أي خطوة مكتملة حتى يتحقق الآتي:

1. إضافة capability جديدة قابلة للاختبار.
2. إضافة/تحديث automated tests المناسبة.
3. تنفيذ manual acceptance check عندما تكون الخطوة UI/runtime.
4. تحديث وثائق architecture/workflow/database/API/UI/testing/ADR المتأثرة.
5. نجاح test suite الحالية وعدم كسر baseline السابق.

## Architectural constraints

- Specialists يعرفهم المستخدم كبيانات، وليسوا classes ثابتة في Python.
- Server Coordinator يدير تحقيق سيرفر واحد.
- Router يختار من Specialists المفعّلين في registry.
- Specialist لا يحصل على arbitrary shell.
- Diagnostic tools مسجلة ومحددة ومعلماتها validated.
- Phase 4 read-only diagnostics فقط.
- Evidence وKnowledge sources قابلة للتتبع.
- Incident RAG وKnowledge RAG لهما أدوار مختلفة.
- التحقيق محدود بـspecialists/rounds/actions budgets.
- Specialists المستقلون يمكن تشغيلهم بالتوازي.
- remediation خارج Phase 4.

## Milestones

### Milestone A — Foundation (4.0–4.4)

المستخدم يستطيع تعريف Specialists والنظام يستطيع تحميلهم والتحقق منهم.

### Milestone B — Routing + Knowledge (4.5–4.9)

النظام يختار Specialists ديناميكيًا ويبني context من current evidence وIncident RAG وKnowledge RAG.

### Milestone C — Single Specialist Investigation (4.10–4.14)

Specialist واحد يستطيع التحقيق بأدوات read-only ضمن budgets.

### Milestone D — Multi-Agent Investigation (4.15–4.18)

عدة Specialists تعمل تحت Server Coordinator، ويمكن إنشاء Specialist إضافي بناءً على الأدلة.

### Milestone E — Productization (4.19–4.20)

واجهة تحقيق كاملة، ثم evaluation وsafety gate.

## Steps

| Step | Capability | Acceptance checkpoint |
|---|---|---|
| 4.0 | Roadmap + ADR baseline | الوثائق تصف الخطة والحدود قبل runtime changes |
| 4.1 | Investigation contracts | إنشاء state/tasks/results/evidence مع invariants وbudgets |
| 4.2 | Dynamic Specialist model + DB | CRUD persistence لتعريف Specialist بدون hard-coded type |
| 4.3 | Specialist management API/UI | إنشاء/تعديل/تعطيل Specialist من الواجهة واستمراره بعد refresh |
| 4.4 | Specialist Registry service | يعيد enabled valid specialists فقط ويكشف التعريفات غير الصالحة |
| 4.5 | Investigation Router | تقرير/تحليل يختار Specialists مناسبين من registry؛ التقرير السليم لا يفتح تحقيقًا غير ضروري |
| 4.6 | Investigation persistence | restart ثم استعادة investigation/tasks/results بدون فقد الحالة |
| 4.7 | Knowledge Sources management | إضافة/تعديل/تعطيل مصدر معرفة وتصنيفه بالmetadata |
| 4.8 | Knowledge RAG | retrieval يعيد معرفة مرتبطة بالمجال مع source attribution |
| 4.9 | Specialist Context Builder | فحص context الفعلي قبل LLM: current evidence + incidents + knowledge + instructions |
| 4.10 | Specialist Reasoning Agent | structured findings/hypotheses/confidence/missing evidence بدون tool execution |
| 4.11 | Diagnostic Tool Registry | tools معروفة، read-only، parameter schemas واضحة، ولا arbitrary shell |
| 4.12 | Diagnostic Policy Engine | allow/deny حسب specialist permissions/tool/risk/parameters/budget |
| 4.13 | Evidence Collection | tool request مسموح ينفذ implementation معروفة وتخزن النتيجة Evidence |
| 4.14 | Specialist Investigation Loop | reason → evidence → reason ضمن max rounds/actions ثم complete/stop |
| 4.15 | Server Coordinator | عدة SpecialistResults لنفس السيرفر تجمع في investigation واحد |
| 4.16 | Parallel Investigation | specialists المستقلون يعملون concurrently بدون state/evidence leakage |
| 4.17 | Dynamic Secondary Specialists | evidence جديدة تستطيع اختيار Specialist إضافي من user-defined registry |
| 4.18 | Correlation + Final Diagnosis | diagnosis نهائي يميز confirmed/probable/unknown وكل claim قابل للتتبع |
| 4.19 | Investigation API/UI | timeline يعرض rounds/tasks/evidence/sources/results/final diagnosis |
| 4.20 | Evaluation & Safety Gate | routing/diagnosis/attribution/latency/cost/safety suite تمر قبل إغلاق Phase 4 |

## Step details and documentation gates

### 4.1 — Investigation Contracts

Scope:
- Investigation state.
- Tasks/results.
- Evidence/knowledge references.
- Findings/hypotheses.
- Budgets/invariants.

Test:
- Unit tests للعقود والحدود والownership.

Docs:
- architecture/investigation contracts.
- roadmap status.

### 4.2 — Dynamic Specialist Model + Database

Scope:
- Specialist definition persisted as user data.
- Suggested fields: slug/name/description/instructions/enabled/domains/trigger hints/knowledge topics/allowed tool IDs/priority/max rounds/max actions.

Test:
- create/read/update/disable.
- unique slug.
- invalid budgets rejected.
- no CPU/Memory/etc. hard-coded specialist class required.

Docs:
- database schema.
- dynamic specialist ADR.
- API model notes.

### 4.3 — Specialist Management API/UI

Scope:
- Specialist list/detail/create/edit/enable-disable.
- Tool selection may remain unavailable until Tool Registry exists.

Test:
- browser/API CRUD.
- refresh persistence.
- validation errors visible.

Docs:
- API.
- UI workflow.
- operator guide.

### 4.4 — Specialist Registry Service

Scope:
- Runtime abstraction over persisted definitions.
- enabled-only lookup.
- domain/capability lookup.
- validation.

Test:
- disabled specialists excluded.
- malformed references rejected.
- registry results deterministic.

Docs:
- architecture/service responsibility.

### 4.5 — Investigation Router

Scope:
- Decide whether investigation is needed.
- Detect issue domains.
- Rank/select from enabled user-defined Specialists.
- Conservative routing.

Test:
- fixtures for CPU, memory, combined, healthy, and no-suitable-specialist cases.

Docs:
- routing workflow.
- routing decision rules.

### 4.6 — Investigation Persistence

Scope:
- Persist investigation lifecycle, tasks, results, evidence, findings as required by observed contracts.

Test:
- save → restart/reload → equivalent state.
- ownership and foreign-key integrity.

Docs:
- database schema.
- lifecycle workflow.

### 4.7 — Knowledge Sources Management

Scope:
- User-defined official/internal/external sources.
- topic/product/version/OS/trust metadata.
- enable/disable lifecycle.

Test:
- CRUD and validation.

Docs:
- knowledge source model.
- trust/source policy.

### 4.8 — Knowledge RAG

Scope:
- Separate technical knowledge retrieval from Incident RAG.
- source attribution and metadata filters.

Test:
- domain relevance.
- incompatible topic/product filtering.
- citations/source IDs preserved.

Docs:
- RAG architecture.
- indexing/retrieval workflow.
- evaluation notes.

### 4.9 — Specialist Context Builder

Scope:
- Build minimal specialist-specific context from task/current evidence/initial analysis/incidents/knowledge/instructions.

Test:
- snapshot/context contract.
- irrelevant evidence excluded.
- source IDs preserved.

Docs:
- context construction workflow.

### 4.10 — Specialist Reasoning Agent

Scope:
- LLM reasoning only.
- Structured result with findings/hypotheses/confidence/ruled-out/missing evidence/recommended specialists.

Test:
- deterministic contract validation using fixtures/mocks where appropriate.
- no tool execution path.

Docs:
- specialist reasoning contract.
- prompt responsibilities.

### 4.11 — Diagnostic Tool Registry

Scope:
- Known read-only diagnostic tools.
- parameter schemas and implementations.
- risk metadata.

Test:
- tool lookup.
- parameter validation.
- unknown/arbitrary tool rejected.

Docs:
- tool registry.
- read-only boundary.

### 4.12 — Diagnostic Policy Engine

Scope:
- Validate specialist permission, tool existence, risk, parameters, and budget.

Test:
- explicit allow/deny matrix.

Docs:
- security policy.
- authorization workflow.

### 4.13 — Evidence Collection

Scope:
- Approved tool → known SSH implementation → Evidence.
- Capture execution metadata and provenance.

Test:
- safe integration test against controlled target/mock.
- denied requests never execute.

Docs:
- SSH/evidence workflow.
- evidence provenance.

### 4.14 — Specialist Investigation Loop

Scope:
- Bounded iterative investigation.

Test:
- two-round diagnosis.
- budget exhaustion.
- no-progress termination.
- failure handling.

Docs:
- state machine.
- budget behavior.

### 4.15 — Server Coordinator

Scope:
- Coordinate specialists for one server.
- collect results and control rounds.

Test:
- CPU + memory scenario.
- partial specialist failure.
- no-specialist scenario.

Docs:
- hierarchical architecture.
- coordinator workflow.

### 4.16 — Parallel Investigation

Scope:
- Concurrent independent specialist execution.

Test:
- no state/evidence cross-contamination.
- timing/performance comparison.
- cancellation/error isolation.

Docs:
- concurrency model.
- performance notes.

### 4.17 — Dynamic Secondary Specialists

Scope:
- New evidence/domains can cause another registry lookup and a new specialist task.

Test:
- PostgreSQL specialist present → spawned.
- PostgreSQL specialist absent/disabled → not fabricated.
- duplicate/loop spawning prevented.

Docs:
- dynamic routing lifecycle.

### 4.18 — Correlation + Final Diagnosis

Scope:
- Correlate specialist findings.
- distinguish confirmed/probable/unknown.
- evidence chain for claims.

Test:
- common-process correlation.
- conflicting specialist results.
- insufficient evidence.

Docs:
- diagnosis contract.
- confidence/evidence semantics.

### 4.19 — Investigation API/UI

Scope:
- Investigation detail/timeline.
- tasks, rounds, evidence, knowledge sources, specialist results, final diagnosis.

Test:
- UI acceptance tests/manual checklist.
- long evidence/source text does not break layout.
- statuses and provenance visible.

Docs:
- UI/API/operator workflow.

### 4.20 — Evaluation & Safety Gate

Scenarios:
- high CPU.
- high memory.
- CPU + memory same process.
- disk full.
- service failure.
- network issue.
- false alarm.
- insufficient evidence.
- conflicting specialists.
- no suitable specialist.
- tool denied.
- budget exhausted.
- unavailable knowledge source.

Metrics:
- routing correctness.
- specialist usefulness.
- diagnostic accuracy.
- source attribution.
- unsupported claims.
- actions/rounds.
- LLM calls.
- latency.
- token/cost profile.
- safety violations.

Exit condition:
Phase 4 closes only when the agreed evaluation and safety thresholds pass.

## Explicitly out of scope

Phase 4 must not introduce autonomous remediation:

```text
NO automatic restart
NO kill process
NO config modification
NO package installation
NO reboot
NO firewall changes
NO arbitrary shell
```

Remediation belongs to Phase 5 with separate permissions, approval, audit, rollback, and safety design.

## Status tracking

| Step | Status |
|---|---|
| 4.0 | Completed when this documentation baseline is applied and reviewed |
| 4.1 | Implemented locally/pending verification against current branch |
| 4.2–4.20 | Planned |

Update this table at the end of every step.
