# منهجية الاختبارات — Multi-Agent Investigation

**الحالة:** المنهجية الرسمية الحالية حتى إغلاق Phase 4.17  
**بيئة الاختبار المرجعية:** Ubuntu Server 22.04.2 amd64 على VMware

نجاح `pytest` وحده لا يكفي لإغلاق خطوة runtime في Phase 4. يجب فصل صحة العقود، وقاعدة البيانات، والاسترجاع، والـLLM، والسياسة الأمنية، وSSH، وClaude-supervised orchestration.

## 1. Automated regression

```powershell
uv run python -m pytest
```

Reference baseline after the latest accepted Phase 4.17 work:

```text
184 passed, 1 warning
```

The remaining warning is the existing Starlette/TestClient deprecation warning.

قاعدة regression: لا ينخفض baseline إلا بتغيير اختبارات مقصود ومُوثق.

## 2. Database verification

بعد أي schema/index/vector change:

```powershell
uv run python tools/bootstrap_database.py --verify-only
```

Phase 4.16/4.17 orchestration acceptance did not require a new database schema.

## 3. Retrieval verification

Incident RAG and Knowledge RAG are tested independently from the LLM.

Historical incidents are context, not proof of current server state.

Knowledge sources explain technology behavior but do not prove a live server condition.

## 4. Provenance tests

Any Evidence/Knowledge ID emitted by reasoning must exist in the context actually supplied to that Specialist.

Unknown IDs fail validation.

## 5. Diagnostic safety

Required negative cases include:

```text
unknown Tool rejected
Tool not assigned rejected
unknown argument rejected
invalid service/path/port rejected
shell injection rejected
Policy DENY never reaches SSH
```

No arbitrary shell is permitted.

## 6. Specialist Investigation Loop acceptance

Example:

```powershell
uv run python tools/dev/run_specialist_investigation.py 2 nginx `
  "Determine whether NGINX is installed/running and what live evidence supports the conclusion." `
  --domains nginx,http,network `
  --max-rounds 3 `
  --max-actions 5
```

Validate:

```text
bounded rounds
bounded actions
duplicate suppression
Evidence propagation
objective discipline
final synthesis
provenance validation
```

## 7. Claude-supervised multi-Specialist acceptance

The native acceptance keeps Claude coordination, Specialist loops, Policy, SSH,
and MCP tool execution real. Use the repository acceptance test and the smoke
entrypoint rather than retired one-off scripts.

Example:

```powershell
uv run python tools/acceptance/smoke_ollama_claude_runtime.py --server-id <server_id>
uv run python -m pytest tests/real_runtime -q
```

Required invariants:

```text
two_or_more_workers
requested_workers_preserved
Claude-supervised_orchestrator
parallel_mode
global_budget_safe
worker_action_sum_safe
quota_budget_safe
each_worker_within_quota
```

## 8. Dynamic secondary acceptance — Phase 4.17

There are two distinct acceptance questions.

### A. Natural recommendation acceptance

```powershell
uv run python -m pytest tests/test_c14_10_claude_observability.py -q
```

This tests whether the real model naturally recommends another Specialist.

Failure to recommend does not necessarily prove orchestration failure; it can be recommendation-quality behavior.

### B. Controlled recommendation acceptance

```powershell
uv run python -m pytest tests/test_specialist_investigation_loop.py -q
```

Only the recommendation value is controlled. Primary/secondary Specialist executions and Phase 4.17 Registry/budget validation remain real.

Accepted reference result:

```text
Status:                  completed
Execution mode:          dynamic-secondary
Waves completed:         2
Actions used:            3/10
Executed Specialists:    nginx, systemd-service
Secondary requested:     systemd-service
Secondary accepted:      systemd-service
```

All Phase 4.17 orchestration acceptance checks passed.

## 9. Ollama structured-output reliability

The deployed model advertises a large context capacity, but the runtime must explicitly configure context.

Reference accepted runtime:

```text
ollama ps
CONTEXT 32768
```

Final Synthesis uses a smaller structured output contract than normal reasoning to reduce truncation and malformed JSON risk.

Test both:

```text
normal reasoning -> rich contract
final synthesis  -> compact contract
```

Do not globally reduce generation limits as a substitute for adequate context.

## 10. Controlled VM ground truth

Required scenarios include:

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

Record false positives and false negatives.

## 11. Budget tests

Test:

```text
max specialists
max rounds
max actions
per-worker parallel quota
context budget
Tool timeout
Tool output limit
duplicate requests
dynamic secondary loops
```

Every limit must stop safely and visibly.

## 12. Step completion gate

A Phase 4 step closes only when all applicable items pass:

```text
1. capability implemented
2. automated tests added
3. full pytest passes
4. previous regressions pass
5. DB verification when schema/index changes
6. runtime acceptance
7. real LLM acceptance when LLM behavior changes
8. retrieval acceptance when retrieval changes
9. safety negative tests when execution changes
10. controlled VM test when live evidence changes
11. documentation updated
12. UI updated only for operator-managed capabilities
```

## 13. Phase 4.18 testing target

Correlation + Final Diagnosis must test:

```text
common-process correlation
conflicting Specialist conclusions
insufficient Evidence
confirmed/probable/unknown classification
claim-to-Evidence traceability
no unsupported global diagnosis
```

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution see `docs/testing/TESTING_STRATEGY.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **TESTING**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
