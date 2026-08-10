# منهجية الاختبارات — Multi-Agent Investigation

**الحالة:** المنهجية الرسمية الحالية حتى Phase 4.11  
**بيئة الاختبار المرجعية:** Ubuntu Server 22.04.2 amd64 على VMware

نجاح `pytest` وحده لا يكفي لإغلاق أي خطوة كبيرة في Phase 4. يجب التمييز بين صحة الكود، وصحة قاعدة البيانات، وصحة الاسترجاع، وسلوك الـLLM، وصحة التشخيص على VM حقيقي.

## 1. Unit / Contract Tests

الأمر الأساسي:

```powershell
uv run python -m pytest
```

الـbaseline الحالي بعد Phase 4.11:

```text
124 passed
```

تشمل هذه الطبقة عقود Investigation، Router rules، parsing/chunking، RRF، context budgets، citation validation، Specialist recommendation normalization، Diagnostic Tool validation، وTool allow-list enforcement.

قاعدة regression: لا ينبغي أن يقل baseline السابق إلا إذا استُبدلت اختبارات بشكل مقصود ومُوثق.

## 2. Database / Schema Verification

```powershell
uv run python tools/bootstrap_database.py --verify-only
```

يجب تشغيله بعد أي تغيير في tables أو columns أو indexes أو vector dimensions أو generated search_vector أو constraints. نجاح migration وحده لا يكفي.

## 3. Runtime Acceptance Tests

تُجرى ضد التطبيق الحقيقي وPostgreSQL وOllama وRegistry وRepositories الفعلية.

أمثلة:

```text
inspect_specialist_registry.py
inspect_investigation_routing.py
persist_investigation_routing.py
inspect_investigation.py
inspect_knowledge_sources.py
ingest_knowledge_source.py
chunk_knowledge_document.py
index_knowledge_document.py
inspect_knowledge_index.py
search_knowledge.py
inspect_specialist_context.py
reason_specialist_context.py
inspect_diagnostic_tools.py
```

كل خطوة Runtime-dependent يجب أن يكون لها أمر قبول واضح ونتيجة متوقعة.

## 4. Retrieval Tests

يجب اختبار Retrieval بصورة مستقلة عن الـLLM.

### Incident RAG

نقيّم semantic similarity، vector ranking، full-text ranking، compatibility gates، semantic thresholds، RRF fusion، وsource report/analysis provenance.

الحادث التاريخي Context وليس Proof لحالة السيرفر الحالية.

### Knowledge RAG

نقيّم source enabled state، document indexed state، specialist/domain scope، vector rank، full-text rank، RRF fusion، deterministic reranking، Top-K budget، chunk attribution، وsource/document provenance.

مثال:

```powershell
uv run python tools/search_knowledge.py `
  "nginx modules configuration" `
  --specialist nginx `
  --domains nginx,http,proxy
```

قاعدة أساسية:

```text
retrieval correctness != corpus quality
```

قد يعمل المحرك بصورة صحيحة بينما المصدر المفهرس ضعيف.

## 5. Large Document / Chunking Tests

ملف PDF من 100 صفحة لا يُرسل كاملًا للـLLM:

```text
Parser
→ Structure-aware Chunker
→ Index
→ Retrieval
→ Top-K relevant chunks
```

نقيّم chunk sizes، section boundaries، page numbers، overlap، duplicate chunks، irrelevant chunk rate، وrelevant chunk recall.

السؤال الحقيقي: هل يمكن استرجاع نصف الصفحة المفيدة من ملف كبير؟

## 6. LLM Contract Tests

### Mocked LLM

نختبر Pydantic output، unknown evidence/knowledge IDs، confidence bounds، missing_evidence، recommendation normalization، وreasoning-only boundary.

### Real LLM Acceptance

مثال:

```powershell
uv run python tools/reason_specialist_context.py `
  nginx `
  "Determine what can be concluded about the NGINX failure from the supplied context." `
  --domains nginx,http,proxy
```

نقيّم السلوك لا النص الحرفي: confidence، دعم findings، source IDs، missing evidence، عدم اختلاق facts، وعدم ادعاء تنفيذ commands.

## 7. Citation / Provenance Tests

أي Finding يعتمد على Evidence يجب أن يشير إلى `evidence_id`، وأي Finding يعتمد على Knowledge يجب أن يشير إلى `knowledge_source_id`.

أي ID غير موجود في Context يجب أن يفشل validation.

## 8. Diagnostic Tool Safety Tests

من Phase 4.11 فما بعد:

```text
unknown Tool rejected
Tool not assigned rejected
unknown argument rejected
invalid service/path/port rejected
shell injection rejected
```

مثال:

```text
nginx; rm -rf /
```

يجب رفضه قبل command rendering.

وعند إضافة Policy/Execution لاحقًا يجب إثبات أن SSH executor لم يُستدعَ أصلًا عند الرفض.

## 9. Controlled VM Ground-Truth Tests

البيئة المرجعية:

```text
Ubuntu Server 22.04.2 amd64
VMware
```

السيناريوهات:

```text
baseline
cpu-high
memory-high
disk-io
network-http
process-churn
application-errors
failed-systemd-service
mixed
```

السيناريو هو Ground Truth ثم نقارن Routing وEvidence وReasoning بما حدث فعليًا.

### Baseline

المتوقع: healthy report، لا Investigation غير ضروري، ولا false critical finding.

### CPU

المتوقع: CPU metrics تتغير، `linux-cpu` مفضل، process evidence مناسب.

### Memory

المتوقع: memory metrics تتغير و`linux-memory` يصبح مناسبًا.

### Failed systemd service

المتوقع: `systemctl --failed` يكتشف الخدمة، `systemd-service` يصبح مناسبًا، وjournal يدعم التشخيص.

### Network / HTTP

المتوقع: listener وconnections وHTTP errors تظهر في الأدلة.

### Mixed

نختبر تعدد الإشارات، candidate ranking، evidence separation، وcontext budgets.

## 10. Test Matrix

لكل سيناريو نسجل:

```text
Scenario ID
Ground Truth
Server ID
Report ID
Analysis ID
Investigation ID
Detected Domains
Candidate Specialists
Selected Specialists
Tools Requested
Evidence Collected
Findings
Hypotheses
Confidence
Expected Diagnosis
Actual Diagnosis
Pass/Fail
Notes
```

## 11. False Positives / False Negatives

False Positive: النظام يدعي مشكلة غير موجودة.

False Negative: المشكلة موجودة لكن النظام لا يكتشفها.

يجب تسجيل النوعين.

## 12. Regression Cases

حالات ثابتة حالية:

```text
Report 825
Expected: should investigate = false
```

```text
Report 807
Expected:
domains = connectivity, network
selected = linux-network
```

## 13. Performance / Cost

عند إضافة Investigation Loop نسجل:

```text
latency
LLM calls
embedding calls
retrieval calls
Tool actions
rounds
context size
tokens/cost when available
```

## 14. Budget Tests

نختبر حدود max specialists، max rounds، max actions، max context chars، max knowledge chunks، max incident contexts، Tool timeout، وTool output limit.

عند بلوغ الحد يجب التوقف بشكل واضح وآمن.

## 15. Step Completion Gate

أي خطوة Phase 4 تعتبر مكتملة فقط إذا تحقق ما ينطبق عليها من التالي:

```text
1. capability implemented
2. automated tests added
3. full pytest passes
4. previous regression cases pass
5. DB verification if schema/index changed
6. runtime acceptance if runtime-dependent
7. real LLM acceptance if LLM behavior changed
8. retrieval acceptance if search changed
9. safety negative tests if permissions/execution changed
10. controlled VM test if real evidence/execution changed
11. documentation updated
12. Admin UI updated only if capability is operator-managed
```

## 16. ما نسجله عند إغلاق كل خطوة

```text
Step number
Files changed
Migration required?
pytest result
DB verification result
Runtime acceptance command/result
LLM provider/model
Reference IDs
Known limitations
Safety result
Next step
```

## 17. Phase 4.20 Final Evaluation

نقيس routing correctness، Specialist selection correctness، diagnostic accuracy، false positive/negative rates، unsupported claim rate، citation accuracy، Knowledge attribution، missing-evidence usefulness، Tool selection/denial correctness، average rounds/actions، latency، LLM calls، token/cost profile، وsafety violations.

لا يمكن إغلاق Phase 4 فقط لأن pytest أخضر؛ يجب أن يثبت النظام على VM الحقيقي أنه يكتشف المشكلة الصحيحة، يختار الوكيل المناسب، يجمع الأدلة الصحيحة، لا يختلق facts، ولا يتجاوز الصلاحيات.
