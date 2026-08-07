# Testing and RAG Evaluation

## الاختبارات
```powershell
uv run python -m pytest
```
Baseline الموثق قبل هذه المرحلة:
```text
20 passed
```

العقود المختبرة تشمل:
- weak vector candidate يرفض حتى مع Full-Text قوي.
- Full-Text-only لا يتجاوز vector threshold.
- RRF score منفصل عن vector similarity.
- structural conflict يرفض high-similarity candidate.
- compatible candidate يقبل.
- duplicate vector/text candidate يصبح context واحدًا.
- reuse policy وstructured compatibility.

## E2E
```powershell
uv run python tools/evaluate_rag.py
```

Baseline:
```text
Completed analyses:             453
REUSE:                          280
ASSISTED:                        17
FULL:                           156
LLM call rate:                38.19%
Exact reuse integrity:       100.00%
Potential reuse miss rate*:    0.00%
Assisted health agreement*:  100.00%
Historical sources evaluated:    50
Current threshold violations:     0
Current future leakage:           0
Current scope violations:         0
Current compatibility failures:   0
HNSW index present:             True
Current invariant status:       PASS
```
`*` diagnostic/proxy metrics وليست precision/recall.

الأداة تفصل legacy rows عن invariants الحالية.
