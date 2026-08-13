# Phase 4 Implementation Plan — Hierarchical Multi-Agent Investigation

<!-- DOC-STATUS: CURRENT -->

**Status: COMPLETED**

## Goal

تحويل النظام من تحليل تقرير منفرد إلى تحقيق هرمي متعدد الوكلاء لكل سيرفر، مع إبقاء التشخيص في Phase 4 ضمن حدود read-only وعدم إدخال remediation.

## Completed architecture

```text
Monitoring Report
      |
Initial Analysis
      |
Investigation Router
      |
Persisted Investigation
      |
Dynamic Specialist Selection
      |
Claude-supervised Specialist Investigation
      |
Evidence + Incident RAG + Knowledge RAG
      |
Cross-Specialist Correlation
      |
Final Diagnosis + Narrative
      |
Runtime Snapshot Persistence
      |
Investigation API/UI
      |
Evaluation + Safety Gate
```

## Delivery rule

كل capability في Phase 4 اعتبرت مكتملة فقط بعد:

1. automated tests مناسبة؛
2. runtime/manual acceptance عندما يلزم؛
3. تحديث الوثائق المتأثرة؛
4. عدم كسر baseline السابق؛
5. الحفاظ على read-only boundary.

## Architectural constraints

- Specialists بيانات operator-managed وليست classes ثابتة.
- Router deterministic قبل LLM reasoning.
- لا يوجد arbitrary shell.
- Diagnostic Tools مسجلة ومعلماتها validated.
- Policy يملك قرار ALLOW/DENY.
- Evidence وKnowledge IDs قابلة للتتبع.
- Incident RAG وKnowledge RAG منفصلان.
- التحقيق محدود بـspecialist/round/action budgets.
- Claude-supervised يستخدم للتنسيق وليس لتجاوز domain boundaries.
- conflicts تبقى ظاهرة.
- Final Diagnosis claims قابلة للتتبع.
- remediation خارج Phase 4.

## Status

| Step | Capability | Status |
|---|---|---|
| 4.0 | Roadmap + ADR baseline | Completed |
| 4.1 | Investigation contracts | Completed |
| 4.2 | Dynamic Specialist model + DB | Completed |
| 4.3 | Specialist management API/UI | Completed |
| 4.4 | Specialist Registry | Completed |
| 4.5 | Investigation Router | Completed |
| 4.6 | Investigation persistence | Completed |
| 4.7 | Knowledge Sources management | Completed |
| 4.8 | Knowledge RAG | Completed |
| 4.9 | Specialist Context Builder | Completed |
| 4.10 | Specialist Reasoning Agent | Completed |
| 4.11 | Diagnostic Tool Registry | Completed |
| 4.12 | Diagnostic Policy Engine | Completed |
| 4.13 | Evidence Collection | Completed |
| 4.14 | Specialist Investigation Loop | Completed |
| 4.15 | Server Coordinator | Completed |
| 4.16 | Parallel Claude-supervised Investigation | Completed |
| 4.17 | Dynamic Secondary Specialists | Completed |
| 4.18 | Correlation + Final Diagnosis | Completed |
| 4.19 | Investigation persistence/read API/UI | Completed |
| 4.20 | Evaluation, Safety & Production Readiness | Completed |

## Phase 4.20 closeout evidence

Accepted aggregate:

```text
Runtime snapshots evaluated: 10
Persisted observations:      50
Safety observations:         30
Total observations:          80
```

All configured readiness metrics passed.

Final state:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Phase 4 complete

Milestone A — Foundation: completed.

Milestone B — Routing + Knowledge: completed.

Milestone C — Single Specialist Investigation: completed.

Milestone D — Multi-Agent Investigation: completed.

Milestone E — Productization / Evaluation: completed.

## Next phase

Phase 5 begins with **Supervised Remediation contracts and approval semantics**.

No write-capable action should be introduced before:

```text
RemediationPlan contract
risk classification
explicit approval
audit trail
before/after Evidence
rollback design
Policy separation from read-only diagnostics
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
