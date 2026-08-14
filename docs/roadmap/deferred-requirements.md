# Deferred Requirements and Evidence Gaps

| Item | Source | Current partial capability | Reason deferred | Acceptance criteria |
|---|---|---|---|---|
| Native Sandbox closure | Spec 5; FR-010 | Phase 6 contracts, validation, attestation checks, deterministic tests | `phase6_readiness.json` conflicts with Phase 6 final report/default real test status | One provenance-backed WSL2 acceptance record shows native isolation, passed validation, Before/After Evidence, verification, restoration, and cleanup. |
| Autonomous live acceptance | Spec 6; FR-015..018 | Phase 7 evaluator, authorization, reservation, execution, recovery, circuit tests | No standalone Phase 7 result artifact is stored | Record candidate eligibility, AUTO_EXECUTE, consumed authorization, successful verification, replay blocked, policy disabled, and restored final state. |
| Application-code location | Spec 7; FR-022 | Grounded diagnosis and Specialist evidence | No dedicated source repository/line locator workflow proven | A controlled test proves a code-linked incident returns file/location/reason without mutation. |
| Social communication | Spec 8; FR-023 | Admin UI/API approval is a local alternative | No Telegram/social adapter | Safe non-production delivery test to configured channel plus audit and retry/secret handling. |
| Predictive analysis | Spec optional 10 | Historical retrieval and readiness observations | No predictive model/forecast contract | Define dataset, horizon, metric, baseline, and acceptance threshold. |
| Proactive maintenance | Spec optional 11 | Monitoring and remediation planning | No proactive scheduler policy proven | A policy-driven maintenance scenario with safety gates and measurable benefit. |
| Long-term trends | Spec optional 12 | Persisted reports/retrieval | No trend aggregation/dashboard contract | Multi-period aggregation, retention, visualization, and benchmark. |
| Decision learning/ranking | Spec optional 13/14 | History and candidates are persisted | No learned ranking model proven | Offline evaluation demonstrates improvement without weakening policy gates. |
| Advanced dashboards | Spec optional 15 | Completed vanilla Admin operational screens | No advanced analytics dashboard requirement implemented | Define user stories, datasets, query limits, and visual acceptance tests. |
| OpenClaw comparison | Spec optional 16 | None | Comparative study is outside current implementation | A separate evidence-based comparison document, if still required. |
| Fresh-machine acceptance | Operations | README/bootstrap/runbooks | No clean-host acceptance record | Rebuild from documented prerequisites and verify schema, MCP, Admin, and safe startup. |

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **ROADMAP**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
