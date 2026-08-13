# Phase C Final Closeout

<!-- DOC-STATUS: CURRENT -->

## Purpose

Phase C consolidated the project around a real Claude Code supervisory runtime
for bounded monitoring and diagnosis. It replaced duplicated workflow surfaces
with one Claude/Ollama/MCP/Python execution boundary and required runtime,
safety, persistence, evaluation, and documentation evidence before Phase 5.

## Final architecture decision

```text
Claude Code = supervisory reasoning and high-level sequencing
Ollama      = operational LLM provider
MCP         = bounded Claude-facing project capability surface
Python      = execution, validation, policy, persistence, evidence, budgets,
              SSH safety, database access, and Admin/API
```

The invariant is:

```text
Claude decides WHAT / NEXT.
Python decides WHETHER ALLOWED and HOW IT IS EXECUTED SAFELY.
```

The canonical application packages are `core`, `capabilities`,
`runtime/claude`, `interfaces`, `infrastructure`, and `composition`. The old
production trees `app/domain`, `app/admin`, `app/mcp`, `app/shared`, and
`app/tools` are absent. No duplicate Python orchestration remains active.

## Runtime contract

Native Claude Code runs the `server-supervisor` contract with the bounded
`specialist-worker` contract when DB-defined Specialist work is required.
Claude uses the project `vps` MCP server and an Ollama-backed model. Python
owns the project capabilities, policy, budgets, Evidence, PostgreSQL
persistence, known-hosts SSH, AgentJobs, and runtime snapshots.

The runtime exposes exactly 24 project MCP tools. No raw SSH, raw SQL,
arbitrary shell, unrestricted filesystem, or generic subprocess capability is
exposed to Claude. Automatic remediation remains disabled.

## C.14.12 readiness evidence

The accepted readiness evidence is documented in
[`c14-12-runtime-readiness-gate.md`](../architecture/c14-12-runtime-readiness-gate.md)
and preserved in `artifacts/evaluation/c14_12_readiness.json`.

```text
runtime sessions:              11
persisted observations:        50
controlled observations:       30
aggregate observations:        80
investigations evaluated:      10
specialist runs:               20
evidence records:              69
controlled failures:           30
```

| Metric | Result | Threshold |
|---|---:|---:|
| routing_recall | 10/10, 1.000 PASS | 0.950 |
| specialist_completion | 10/10, 1.000 PASS | 0.900 |
| evidence_grounding | 10/10, 1.000 PASS | 1.000 |
| budget_compliance | 10/10, 1.000 PASS | 1.000 |
| conflict_preservation | 10/10, 1.000 PASS | 1.000 |
| final_diagnosis_grounding | 10/10, 1.000 PASS | 1.000 |
| provider_resilience | 10/10, 1.000 PASS | 0.950 |
| policy_safety | 10/10, 1.000 PASS | 1.000 |

Overall readiness: **8/8 PASS**.

## Final real runtime acceptance

The final opt-in acceptance used server 2 and model
`gemma4:e4b-it-q4_K_M`:

```text
job_id:       0c4c5053-8994-4f71-ae06-5f7ec9314dff
session_id:   0a9bc785-5148-4540-9618-418bf37d55be
server_id:    2
report_id:    1805
analysis_id:  1636
investigation_id: none required by persisted analysis
MCP:          vps connected
turns/calls:  7 / 6
status:       accepted / completed
```

The real report outcome was `connection_failed`; the analysis was completed
through persisted reuse with `llm_called=false`, and the result was accepted as
a controlled failure rather than fabricated success. The prior C.14.12
acceptance also exercised persisted investigation routing.

## Test results

```text
architecture tests:       6 passed
C.14.12 focused tests:   26 passed
normal full suite:      417 passed, 1 skipped, 1 warning
real runtime acceptance: 1 passed in 84.02 seconds
```

The warning is the existing Starlette/httpx deprecation warning. Controlled
safety evaluation passed all 30 routing/provider/policy observations.

## Safety guarantees

- Policy cannot be bypassed by Claude or Specialist workers.
- Evidence references are ownership-validated and fail closed.
- Specialist, investigation, turn, tool-call, action, and timeout budgets are
  enforced.
- SSH requires the configured private key and `known_hosts`.
- Raw SSH, raw SQL, arbitrary shell, and unrestricted filesystem access are not
  MCP capabilities.
- Provider, MCP, database, SSH, and policy failures produce controlled failure
  outcomes without unsafe fallback.
- `automatic_remediation_allowed = false`.

## Known limitations and technical debt

The real acceptance uses external PostgreSQL, Ollama, Claude CLI, MCP, SSH
credentials, and a managed VPS; normal tests do not replace those services.
The current real acceptance intentionally proves controlled diagnostic failure
semantics and does not execute production remediation. The Starlette/httpx
warning remains for later dependency maintenance.

## Phase C gate

```text
C.14.14 = PASS
PHASE C = CLOSED
```

Phase 5 — Supervised Remediation is the next allowed phase. This closeout does
not implement Phase 5.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **ROADMAP**

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
