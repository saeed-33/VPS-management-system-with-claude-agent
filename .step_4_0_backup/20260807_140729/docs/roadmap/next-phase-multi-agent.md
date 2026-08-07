# Next Phase: Hierarchical Multi-Agent Investigation

**Status: Proposed — NOT IMPLEMENTED**

## الفكرة
لكل سيرفر `Server Coordinator` يدير التحقيق. عند وجود مشكلة ينشئ Specialists حسب الحاجة:

```text
Server Coordinator
   +-- CPU Specialist
   +-- Memory Specialist
   +-- Disk/Network/Service/... Specialist
```

مثال: CPU وMemory مرتفعان -> وكيلان بالتوازي -> كلاهما يحدد نفس PostgreSQL process -> المنسق ينشئ PostgreSQL Specialist -> correlation -> final diagnosis.

## RAG
- **Incident RAG:** الحالات التاريخية، امتداد للمنظومة الحالية.
- **Knowledge RAG:** وثائق رسمية، runbooks، SOPs وknown issues مع metadata مثل topic/product/version/OS/source/trust.

## قيود التصميم
- لا shell مفتوح للـLLM.
- أدوات تشخيصية مسجلة ومعلمات validated.
- البداية read-only.
- كل Evidence محفوظ وقابل للتتبع.
- Server Coordinator مسؤول عن correlation.
- budgets لعدد specialists/rounds/actions.
- يمكن تشغيل specialists المستقلين بالتوازي.
- remediation مرحلة مستقلة لاحقة.

## الخطة
```text
4.1 Investigation State + Contracts
4.2 Specialist Registry
4.3 Investigation Router
4.4 Knowledge RAG
4.5 Diagnostic Tool Registry
4.6 Specialist Agent
4.7 Server Coordinator Agent
4.8 Bounded Investigation Loop
4.9 Investigation UI
4.10 Evaluation
```
