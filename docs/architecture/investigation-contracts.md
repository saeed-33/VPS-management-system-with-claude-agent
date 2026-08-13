# 4.1 — Investigation State and Multi-Agent Contracts

**Status: Implemented contract baseline**

هذه الخطوة لا تشغّل Agents ولا SSH ولا LLM جديدًا. هي تعرف لغة البيانات المشتركة التي ستستخدمها المرحلة متعددة الوكلاء.

## الهدف

منع انتقال المرحلة الرابعة إلى تبادل نصوص حرة بين الوكلاء. كل Server Coordinator وSpecialist سيعملان على عقود صريحة وقابلة للاختبار.

## العقود

### ServerInvestigationState

الحالة المركزية لتحقيق سيرفر واحد:

```text
investigation_id
server_id
report_id
analysis_id
status
round_number
budget
detected_domains
evidence
knowledge_sources
tasks
results
final_findings
metadata
```

التحقيق مربوط بسيرفر وتقرير محددين.

### InvestigationBudget

الحدود الافتراضية:

```text
max_specialists = 4
max_rounds      = 3
max_actions     = 12
```

`max_actions` معرف في العقد منذ الآن لكنه لن يستهلك فعليًا قبل بناء Diagnostic Tool execution.

### SpecialistTask

طلب من Server Coordinator إلى Specialist:

```text
task_id
investigation_id
server_id
report_id
specialist_id
objective
trigger_issue_ids
evidence_ids
knowledge_topics
round_number
status
```

`specialist_id` نص وليس Enum. قائمة التخصصات ستكون مسؤولية 4.2 Specialist Registry.

### SpecialistResult

النتيجة المنظمة للمتخصص:

```text
task_id
specialist_id
status
summary
confidence
findings
hypotheses
ruled_out
evidence_ids
knowledge_source_ids
recommended_next_specialists
```

### EvidenceReference

مرجع لدليل، وليس shell output غير منظم داخل state.

أنواع الأدلة الحالية:

```text
monitoring_report
command_result
analysis
historical_incident
knowledge_document
derived_finding
```

### KnowledgeSourceReference

يمثل مصدرًا معرفيًا مع metadata قابلة للتوسع:

```text
source_type
title
url
topic
product
version
trust_level
excerpt
metadata
```

أنواع المصدر:

```text
incident
internal_document
official_documentation
external_reference
```

### Finding / Hypothesis

كلاهما يحمل confidence بين `0.0` و`1.0`.

Finding يرتبط بـevidence/knowledge source IDs.
Hypothesis يستطيع تسجيل أدلة مؤيدة وأدلة معارضة.

## Invariants

`ServerInvestigationState` يفرض حاليًا:

- لا duplicate evidence IDs.
- لا duplicate knowledge source IDs.
- لا duplicate task IDs.
- كل task يجب أن يكون لنفس investigation/server/report.
- task لا يتجاوز max round.
- عدد unique specialists لا يتجاوز budget.
- result يجب أن يشير إلى task معروف.
- result specialist يجب أن يطابق task specialist.
- result واحد فقط لكل task.
- Pending ليست حالة صالحة لـSpecialistResult.

## لماذا لا توجد قاعدة بيانات في 4.1؟

هذه الخطوة تثبت Domain Contract أولًا. Persistence سيأتي بعد أن نثبت شكل التحقيق ونحدد lifecycle المطلوب، حتى لا ننشئ schema مبكرًا ثم نغيره أثناء 4.2/4.3.

## لماذا لا يوجد Specialist Enum؟

لأن 4.2 سيبني Specialist Registry. إذا جعلنا الأنواع Enum الآن فكل إضافة تخصص ستتطلب تعديل contract، بينما المطلوب أن يستطيع Registry إضافة تخصصات ضمن عقد ثابت.

## الخطوة التالية

4.2 — Specialist Registry:

- تعريف specialist capabilities.
- allowed evidence topics.
- allowed tool IDs مستقبلًا.
- knowledge retrieval topics.
- routing metadata.
- registry validation.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
