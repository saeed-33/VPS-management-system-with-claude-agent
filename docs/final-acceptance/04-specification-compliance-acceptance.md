# 04 - Specification Compliance Acceptance

## 1. Objective

Audit the minimum specification functions 1-9 literally against the current
repository. The authoritative specification inputs found in the repository
are `docs/requirements/specification-compliance.md`,
`docs/requirements/functional-requirements.md`,
`docs/requirements/traceability-matrix.md`, and the related use cases. No
separate specification file with a different requirement set was found.

This record is the final acceptance disposition for the mandatory functions
and records the bounded implementation and deterministic acceptance work that
closed SPEC-03, corrected SPEC-05 traceability, and closed SPEC-07.

## 2. Chronological project-owner decision

The original literal audit recorded `SPEC_08_DEVELOPER_SOCIAL_NOTIFICATION =
FAIL` because no Telegram or other social-messaging adapter exists. On
2026-08-14, after that audit, the project owner explicitly decided not to
implement Telegram or any social-messaging notification adapter in the current
release. The owner accepted this as an intentional project-scope deviation.

This decision does not relabel requirement 8 as PASS and does not change
`MANDATORY_SPECIFICATION_COMPLIANCE = FAIL`. It changes the project-readiness
disposition only: the deviation is accepted and is not a technical,
architecture, or project-closure blocker. The existing Admin approval workflow
remains the human approval mechanism, but is not literal social-channel
compliance.

On 2026-08-14, SPEC-03 and SPEC-07 were implemented with small additive
contracts on the existing analysis, Evidence, Investigation, policy, and
read-model paths. SPEC-05 was changed from PARTIAL to PASS by traceability
correction against the already closed Phase 6 evidence; no Phase 6 code or
real acceptance was reopened or rerun. The implementation did not add a
database table or migration, change MCP responsibilities, or implement social
notification.

## 2. Acceptance constraints

- The local repository and existing acceptance records are authoritative.
- No Phase 5/6/7 orchestration semantics were modified for this acceptance
  update; the requested additive SPEC-03/SPEC-07 paths are recorded below.
- Phase 5 real, Phase 6 real, Phase 7 real, and Specialist real acceptance
  runs were not rerun.
- Existing Phase 6 and Phase 7 records were inspected, including the current
  final Phase 7 real acceptance record.
- Optional functions 10-16 are recorded for completeness and are not closure
  blockers.

## 3. Requirement-by-requirement disposition

### Requirement 1 - Server monitoring: PASS

CPU, memory, storage, services, and system-log collection are represented by
registered bounded monitoring/diagnostic commands. `MonitoringService` uses
the configured server/profile, executes through the bounded SSH command path,
persists reports and command results, and maps connection/unexpected failures
to controlled report outcomes. `MonitoringScheduler` supplies periodic
supervisory invocation. The diagnostic-tool registry includes service status,
journal, CPU/memory process views, memory, vmstat, filesystem, path, and inode
signals.

Traceability is `FR-001..003` -> `UC-001..004` -> monitoring services,
`SSHCommandExecutor`, report repositories, and scheduler -> Admin/configured
profiles and persisted reports -> `tests/test_evidence_collection.py`,
`tests/test_investigation_router.py`,
`tests/test_claude_supervisor.py::test_supervisor_delegates_monitoring_cycle`,
`tests/test_project_mcp_tool_boundary.py::test_get_monitoring_profile_includes_commands`,
and `tests/test_project_mcp_tool_boundary.py::test_run_monitoring_invokes_existing_service_and_reads_report`
-> the Admin monitoring/profile acceptance, Specialist service/log evidence,
and existing monitoring/report controlled-error evidence. The deterministic
tests establish collection/error behavior; the final real acceptance records
are downstream remediation/evidence records, not a claim that every signal
was re-collected during this audit.

### Requirement 2 - Intelligent error analysis: PASS

The implementation contains the Claude supervisory flow, Ollama-backed
operational reasoning, report analysis, hybrid retrieval/RAG context,
Investigation routing, DB-defined Specialists, owned Evidence persistence, and
grounded diagnosis synthesis. This is not being inferred from deterministic
monitoring alone. The final Specialist record documents real Ollama reasoning,
real Claude Specialist flow, canonical Specialist persistence, and project-owned
Evidence persistence, with the accepted bounded-finalization limitation.

Traceability is `FR-004..008` -> `UC-005..008` -> analysis orchestrator,
retrieval/RAG, Ollama client, investigation router/loop, Evidence collection,
and final diagnosis synthesizer -> persisted analysis, investigation,
Specialist, Evidence, and diagnosis contracts ->
`tests/test_hybrid_retriever.py`, `tests/test_final_diagnosis_synthesizer.py`,
`tests/test_investigation_router.py`,
`tests/test_project_mcp_analysis_tools.py`,
`tests/test_project_mcp_investigation_tools.py`, and Specialist persistence
tests -> `02-specialist-final-e2e-acceptance.md` and its recorded real IDs.

### Requirement 3 - Error severity classification: PASS

`ErrorClassification` is the explicit persisted domain classification with
exact values `normal`, `dangerous`, and `sensitive`. It is separate from
`AnalysisSeverity` (`info`, `warning`, `critical`) and `RemediationRisk`
(`low`, `medium`, `high`, `critical`). Deterministic classification examines
the issue title, description, Evidence text, and recommendation. Sensitive
markers (credentials, secrets, tokens, authentication/security findings,
protected paths, and permission/access indicators) take precedence. Dangerous
markers (outage, production/service failure, data loss/corruption, disk full,
OOM, crash, unavailable, and resource exhaustion) produce `dangerous` when no
sensitive marker is present. Everything else is `normal`; severity or action
risk alone is not silently remapped.

The classifier runs before canonical analysis JSON persistence and normalizes
reused analysis rows on copy, so classification survives reload without a DB
migration. The autonomous policy consumes the persisted plan classification:
`normal` remains subject to all existing Phase 7 gates, while `dangerous` and
`sensitive` are deterministic deny outcomes even when action risk is `low`.
The report analysis API already returns issue dictionaries and the Admin
report UI renders the classification badge.

Traceability is `FR-005` -> `UC-005`, `UC-008`, and `UC-018` -> analysis
contract/classifier, repository persistence, remediation plan metadata, and
autonomous policy -> report API/UI and policy decisions ->
`tests/test_error_classification.py`,
`tests/test_error_classification_policy.py`, existing routing tests, and the
full non-real regression. Status: PASS. Architectural impact: NONE.

### Requirement 4 - Solution generation: PASS

`RemediationService.create_plan` accepts a diagnosis and owned Evidence,
validates registered actions, derives risk, creates a fingerprinted proposal,
and persists it. Unsupported actions and no-solution outcomes are represented
as controlled results. The plan carries action, rationale/context, risk, and
Evidence/diagnosis bindings for the supervised and autonomous paths.

Traceability is `FR-009` -> `UC-009` -> remediation service, action registry,
plan repository, and MCP/Admin remediation surfaces -> persisted immutable plan
and fingerprint -> `tests/test_phase5_supervised_remediation.py`,
`tests/test_phase5_admin_api.py`, and
`tests/test_project_mcp_remediation_tools.py` -> Phase 5 real acceptance and
Admin acceptance evidence.

### Requirement 5 - Isolated solution testing: PASS

The Phase 6 native Sandbox implementation exists. It performs native runtime
execution, attestation, plan-fingerprint binding, Before/After Evidence,
stale/mismatch validation, and fail-closed handling; the code has no approved
unsandboxed fallback. Deterministic coverage exists in
`tests/test_phase6_native_sandbox_runtime.py` and
`tests/test_phase6_sandbox_validation.py`.

The canonical Phase 6 harness and closed evidence establish native sandbox
attestation, exact registered action execution, Before/After Evidence,
expected-state verification, reverse action, restoration Evidence,
original-state restoration, fingerprint binding, stale protection, and
fail-closed behavior without an unsandboxed fallback. The earlier PARTIAL was
stale traceability. `STATUS CHANGE REASON = TRACEABILITY CORRECTION`.
`PRODUCTION CHANGE = NONE`; `PHASE 6 REOPENED = NO`; `REAL ACCEPTANCE RERUN =
NO`. Architectural impact: NONE.

### Requirement 6 - Automatic application of safe solutions: PASS

The current final real Phase 7 record is `PASS`. The implementation limits
automatic execution to the explicit low-risk/hard-allowlist policy boundary,
requires the global kill switch, policy/history/sandbox/Evidence and exact
binding checks, and uses authorization consumption, reservation/idempotency,
execution, verification, rollback, and failure/circuit handling.

The final real evidence is `docs/final-acceptance/01-final-phase7-real-acceptance.md`:
execution succeeded, the policy ended disabled, the final state was restored,
verification was verified, 18 executions succeeded with zero failures, and
replay was blocked. The recorded IDs include the authorization, plan,
decision, execution, issue fingerprint, policy, reservation, and Sandbox
validation. The global setting remains disabled by default; the acceptance
used an explicitly scoped test opt-in. This is a safety control, not a gap in
the bounded requirement.

Traceability is `FR-012`, `FR-015..018` -> `UC-012..020` -> autonomous policy
evaluator, execution service, authorization, reservation, runtime, and
rollback services -> persisted decision/authorization/reservation/execution/
Evidence/audit surfaces -> `tests/test_autonomous_remediation_policy.py`,
`tests/test_autonomous_remediation_authorization.py`,
`tests/test_autonomous_execution_idempotency.py`,
`tests/test_phase7_negative_security.py`, and
`tests/test_phase7_concurrency_recovery.py` -> final Phase 7 real acceptance.

### Requirement 7 - Application-code error location: PASS

`SourceLocation` is the structured contract with `file_path`, `line_number`,
optional `column_number`, `module`, `function`, and `exception_type`, plus
`reason`, `source`, and `evidence_ids`. The bounded deterministic extractor
supports Python traceback frames with terminal exception type/message and
allowlisted generic `path:line[:column]` forms for common application source
extensions. It rejects SSH transport errors, malformed text, and arbitrary
numeric log output.

Locations are extracted from project-owned command Evidence, bound to the
exact Evidence ID, copied only for Evidence IDs referenced by a Specialist
finding, and propagated into correlated claims and final-diagnosis metadata.
The existing runtime snapshot persistence reloads this structured metadata;
the Investigation API/read model returns it and the Admin Investigation UI
renders file and line. No new table or migration was needed.

Traceability is `FR-022` -> `UC-008` -> Evidence collection, Specialist
finding enrichment, correlation/final diagnosis, runtime snapshot, API/read
model, and Admin UI -> `tests/test_source_location.py`,
`tests/test_investigation_runtime_snapshot_service.py`,
`tests/test_investigations_api.py`, and the full non-real regression. Status:
PASS. Architectural impact: LOW.

### Requirement 8 - Developer social notification: FAIL

No outbound Telegram or other explicitly implemented social/messaging adapter
was found. The Admin UI/API is a local approval channel and is not equivalent
to the required developer social communication channel. Consequently there
is no proven configurable developer recipient, sanitized dangerous/sensitive
proposal payload delivery, persisted delivery failure/audit path, or explicit
no-execution-authority notification boundary.

Traceability is `FR-023` -> `UC-021` -> future notification adapter -> no
production implementation, persistence, API, UI, MCP, automated test, or
real/manual delivery evidence. This remains a production-code gap and is
recorded as `NOT_IMPLEMENTED` by explicit project-owner decision. It remains a
literal specification FAIL, but is an accepted project deviation:
`SPEC_08_ACCEPTED_PROJECT_DEVIATION = YES`,
`SPEC_08_TECHNICAL_BLOCKER = NO`, and
`SPEC_08_ARCHITECTURE_BLOCKER = NO`. It does not block current project
closure. The smallest future compliance fix would be a notification port and
one configured adapter, recipient configuration, secret-free proposal/context
serialization, persisted delivery failure/audit records, and a boundary test
proving the adapter cannot execute remediation. Do not implement that adapter
in this audit. Architectural impact of that future fix: MEDIUM.

### Requirement 9 - Developer approval before risky execution: PASS

The supervised flow persists a pending approval, supports approve/reject and
expiration, binds approval to the exact plan fingerprint and scope, checks
authorization/RBAC/CSRF, records actor/audit data, and permits execution only
after valid approval. Stale, mismatched, rejected, expired, or unauthorized
paths fail closed. Manual/no-action outcomes remain available through the
approval lifecycle. The autonomous evaluator cannot bypass approval for
dangerous/high-risk actions: its safe automatic scope is policy-gated low risk;
otherwise it returns approval-required or deny.

Traceability is `FR-011..012` and `NFR-SEC-001..002` -> `UC-011..015` and
`UC-024..026` -> `RemediationService`, repositories, Admin auth/RBAC,
remediation API/UI, and autonomous policy -> approval/execution/negative
security tests -> `docs/roadmap/phase-5-final-report.md` real Phase 5 PASS,
`docs/final-acceptance/03-admin-ui-manual-acceptance.md`, and deterministic
Admin/remediation tests.

## 4. Cross-requirement traceability matrix

| SPEC ID | ORIGINAL REQUIREMENT | INTERNAL FR | USE CASE | IMPLEMENTATION | TESTS | FINAL ACCEPTANCE EVIDENCE | STATUS | GAP |
|---|---|---|---|---|---|---|---|---|
| SPEC-01 | Monitor CPU, memory, storage, services, and system logs. | FR-001..003 | UC-001..004 | Monitoring profiles/commands, SSH executor, scheduler, reports, persistence. | `tests/test_evidence_collection.py`; `tests/test_investigation_router.py`; `tests/test_claude_supervisor.py::test_supervisor_delegates_monitoring_cycle`; `tests/test_project_mcp_tool_boundary.py::test_get_monitoring_profile_includes_commands`; `tests/test_project_mcp_tool_boundary.py::test_run_monitoring_invokes_existing_service_and_reads_report`. | Admin monitoring/profile acceptance; Specialist service/log evidence; existing monitoring/report controlled-failure evidence. | PASS | No acceptance rerun required for this audit. |
| SPEC-02 | Analyze errors/problems using an intelligent agent. | FR-004..008 | UC-005..008 | Claude supervisor, Ollama analysis, RAG/retrieval, Investigation, Specialists, Evidence, diagnosis. | Hybrid retrieval, diagnosis, investigation, analysis MCP, and Specialist persistence tests. | `02-specialist-final-e2e-acceptance.md`; real Ollama PASS and real Claude flow PASS with accepted bounded limitation. | PASS | Final Claude completion is separately PARTIAL but does not remove the proven intelligent flow. |
| SPEC-03 | Classify severity as normal, dangerous, or sensitive. | FR-005 | UC-005, UC-008, UC-018 | `ErrorClassification`, deterministic classifier, persisted issue metadata, plan metadata, autonomous policy, report API/UI. | `tests/test_error_classification.py`; `tests/test_error_classification_policy.py`; routing and full regression. | Classification persisted/reloaded; dangerous/sensitive denied from autonomous low-risk path. | PASS | Separate from severity and remediation risk; no migration. |
| SPEC-04 | Generate suitable grounded remediation proposals. | FR-009 | UC-009 | Remediation service, action registry, diagnosis/Evidence binding, fingerprinted plan repository. | Phase 5 supervised/Admin and MCP remediation tests. | Phase 5 real PASS and Admin acceptance. | PASS | None identified. |
| SPEC-05 | Test proposed solutions in an isolated environment before application. | FR-010, NFR-SEC-005 | UC-010 | Native Sandbox runtime, attestation, fingerprint/stale checks, Evidence, fail-closed policy. | `tests/test_phase6_native_sandbox_runtime.py`; `tests/test_phase6_sandbox_validation.py`; canonical `tests/real_runtime/test_phase6_real_sandbox_acceptance.py`. | Existing closed Phase 6 evidence covers isolated execution, verification, reverse action, restoration, and fail-closed controls. | PASS | STATUS CHANGE REASON = TRACEABILITY CORRECTION; production change none; Phase 6 not reopened or rerun. |
| SPEC-06 | Automatically apply safe solutions for normal errors. | FR-012, FR-015..018 | UC-012, UC-017..020 | Low-risk allowlist, kill switch, policy/history, Sandbox/Evidence, auth, reservation, execution, verification, rollback. | Autonomous policy/auth/idempotency/negative-security/recovery tests. | `01-final-phase7-real-acceptance.md`: PASS; 18/18 verified, restored, replay blocked. | PASS | None in the bounded accepted scope. |
| SPEC-07 | Locate hosted application-code errors and explain the reason. | FR-022 | UC-008 | `SourceLocation`, bounded traceback/path-line parser, Evidence binding, finding/claim/final-diagnosis metadata, snapshot/API/UI. | `tests/test_source_location.py`; `tests/test_investigation_runtime_snapshot_service.py`; `tests/test_investigations_api.py`; full regression. | Python and generic source locations are reason- and Evidence-bound and survive runtime snapshot/API reload. | PASS | No new table or migration; bounded parser only. |
| SPEC-08 | Send dangerous/sensitive proposals through developer social communication. | FR-023 | UC-021 | No outbound social adapter; Admin/API is local only. | No implementation or delivery test. | No delivery evidence; owner explicitly accepted non-implementation. | FAIL | Literal requirement remains absent, but accepted project deviation means no current technical, architecture, or closure blocker. |
| SPEC-09 | Obtain developer approval before risky execution or offer manual alternative. | FR-011..012, NFR-SEC-001..002 | UC-011..015, UC-024..026 | Persisted approval service/repository, RBAC/CSRF API/UI, exact binding, execution gate, autonomous deny/approval policy. | Phase 5 supervised/Admin, Admin auth/RBAC, remediation API, and negative-security tests. | Phase 5 real PASS and Admin manual acceptance PASS. | PASS | None identified for dangerous/high-risk supervised execution. |

The matrix is complete as an acceptance matrix. The older requirements matrix
uses coarser grouped statuses and records requirement 8 as `DEFERRED`; this
record supersedes those coarse labels for the literal final disposition. The
owner decision changes the accepted-deviation disposition of requirement 8,
not its literal FAIL status.

## 5. Optional functions 10-16

| Optional ID | Function | Status | Closure impact |
|---:|---|---|---|
| 10 | Predictive failure analysis | NOT IMPLEMENTED | Not a closure blocker. |
| 11 | Proactive maintenance | NOT IMPLEMENTED | Not a closure blocker. |
| 12 | Long-term trend analytics | NOT IMPLEMENTED | Not a closure blocker. |
| 13 | Learning from developer decisions | NOT IMPLEMENTED | Not a closure blocker. |
| 14 | Ranking from developer decisions | NOT IMPLEMENTED | Not a closure blocker. |
| 15 | Advanced visual dashboards | PARTIAL; vanilla operational Admin screens exist, advanced analytics are not implemented. | Not a closure blocker. |
| 16 | OpenClaw comparison | DEFERRED | Not a closure blocker. |

## 6. Documentation/report consistency

The requirements and roadmap documents correctly identify the major Phase 6,
7, application-code-location, and social-communication evidence areas, but
some older coarse labels still say `IMPLEMENTED` for severity and `DEFERRED`
for social communication. This acceptance record is the literal final
disposition and does not silently convert those labels into PASS. The
chronologically later owner decision accepts requirement 8 as a project
deviation without claiming compliance.

`docs/report/README.md` states that final acceptance records are canonical and
does not claim that the missing mandatory requirements are fully implemented.
No report compliance mismatch was found in the repository report material:
`REPORT_COMPLIANCE_MISMATCH = NO`.

## 7. Final disposition

```text
SPEC_01_SERVER_MONITORING = PASS
SPEC_02_INTELLIGENT_ANALYSIS = PASS
SPEC_03_SEVERITY_CLASSIFICATION = PASS
SPEC_04_SOLUTION_GENERATION = PASS
SPEC_05_ISOLATED_VALIDATION = PASS
SPEC_06_SAFE_AUTO_REMEDIATION = PASS
SPEC_07_CODE_ERROR_LOCATION = PASS
SPEC_08_DEVELOPER_SOCIAL_NOTIFICATION = FAIL
SPEC_09_HUMAN_APPROVAL = PASS

MANDATORY_SPECIFICATION_COMPLIANCE = FAIL

SPEC_08_GAP = No outbound social/messaging adapter sends dangerous/sensitive proposals to a configurable developer recipient with sanitized payloads, persisted delivery failure/audit, and no execution authority.

SPEC_08_IMPLEMENTATION_DECISION = NOT_IMPLEMENTED
SPEC_08_DECISION_TYPE = ACCEPTED_PROJECT_DEVIATION
SPEC_08_ACCEPTED_PROJECT_DEVIATION = YES
SPEC_08_PROJECT_CLOSURE_BLOCKING = NO
SPEC_08_TECHNICAL_BLOCKER = NO
SPEC_08_ARCHITECTURE_BLOCKER = NO

ORIGINAL_SPEC_LITERAL_COMPLIANCE = FAIL

SPEC_03_CLASSIFICATION_CONTRACT = ErrorClassification(normal|dangerous|sensitive), persisted on AnalysisIssue and copied into remediation plan metadata.
SPEC_03_SENSITIVE_SEMANTICS = Credential/secret/token/authentication/security/protected-path/permission-access markers; sensitive takes precedence over dangerous.
SPEC_03_PERSISTENCE = PASS
SPEC_03_POLICY_INTEGRATION = PASS
SPEC_03_API_UI = PASS
SPEC_03_PRODUCTION_CHANGE_REQUIRED = YES
SPEC_03_CLOSURE_BLOCKING = NO

SPEC_05_STATUS_CHANGE_REASON = TRACEABILITY CORRECTION
SPEC_05_PRODUCTION_CHANGE_REQUIRED = NO
SPEC_05_PHASE6_REOPENED = NO
SPEC_05_REAL_ACCEPTANCE_RERUN = NO
SPEC_05_CLOSURE_BLOCKING = NO

SPEC_07_SOURCE_LOCATION_CONTRACT = SourceLocation(file_path,line_number,column_number?,module?,function?,exception_type?,reason,source,evidence_ids)
SPEC_07_SUPPORTED_FORMATS = Python traceback File path/line/in function plus terminal exception; allowlisted path:line[:column] for application source extensions.
SPEC_07_TRACEBACK_EXTRACTION = PASS
SPEC_07_REASON_BINDING = PASS
SPEC_07_EVIDENCE_BINDING = PASS
SPEC_07_PERSISTENCE = PASS
SPEC_07_API_UI = PASS
SPEC_07_PRODUCTION_CHANGE_REQUIRED = YES
SPEC_07_CLOSURE_BLOCKING = NO

OPTIONAL_10_16_STATUS = 10-14 NOT IMPLEMENTED; 15 PARTIAL; 16 DEFERRED; optional gaps do not block project closure.

TECHNICAL_IMPLEMENTATION_BLOCKERS_FROM_SPEC = NONE
ORIGINAL_SPEC_LITERAL_COMPLIANCE = FAIL
FOCUSED_REGRESSION = 110 passed
FULL_NON_REAL_REGRESSION = 620 passed, 4 skipped (624 collected)
MCP_TOOL_COUNT = 25
CLAUDE_ADMIN_SEPARATION = PASS
COMPILEALL = PASS
GIT_DIFF_CHECK = PASS
TRACEABILITY_MATRIX = PASS
REPORT_COMPLIANCE_MISMATCH = NO
DOCUMENTATION_UPDATED = PASS
GIT_DIFF_CHECK = PASS
```

The literal mandatory specification compliance gate remains FAIL because
requirement 8 is unimplemented. Requirements 3, 5, and 7 are now PASS with
no technical implementation blockers.
The owner has accepted requirement 8 as a project deviation, so it is not a
technical, architecture, or project-closure blocker. Requirements 3, 5, and 7
are closed PASS acceptance items. These are reported compliance dispositions,
not a finding that the accepted Specialist limitation is a product defect.
The bounded implementation files and acceptance tests are listed above; no
architecture, Phase 5/6 execution semantics, Claude/Ollama/MCP boundary, or
social-notification behavior was changed. Phase 7 adds only the requested
dangerous/sensitive classification deny gate; existing low-risk policy,
Sandbox, Evidence, history, authorization, and rollback gates are unchanged.

## 8. Whether production code changed

Production code changed only for the requested additive SPEC-03/SPEC-07
contracts and persistence/read paths. No Phase 6 production code changed.

## 9. Whether commit/push occurred

No commit or push occurred.

## 10. Current-worktree Phase 7 disposition

The current worktree was reviewed on 2026-08-14 after SPEC-03 introduced
explicit denial of dangerous and sensitive autonomous proposals.

`CURRENT_WORKTREE_REAL_PHASE7_ACCEPTANCE = PASS`

The safe real autonomous-remediation path remained operational. Phase 7 was
not reopened or rerun for the deployment-security audit. No production
orchestration defect was identified and no architecture change is justified.
