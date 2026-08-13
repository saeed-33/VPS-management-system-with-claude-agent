# C.14.12 Runtime Readiness Gate

This document records the C.14.12 evaluation of the current Claude Code +
Ollama + project MCP runtime. It does not authorize C.14.13, C.14.14, or
Phase 5 work.

## Methodology

The gate combines two evidence layers:

1. Real persisted runtime observations read from the existing Investigation
   runtime snapshots and AgentJob observability projection.
2. Controlled deterministic evaluation using the real router, policy engine,
   Ollama client parsing/retry logic, MCP registry, and grounding validators.

The eight thresholds are the accepted thresholds already defined in
`tools/acceptance/evaluation/readiness_gate.py`; no threshold was lowered.

## Observation counts

The generated machine-readable report is
`artifacts/evaluation/c14_12_readiness.json`.

```text
runtime_sessions:                 11
persisted_runtime_observations:   50
controlled_safety_observations:   30
aggregate_observations:           80
reports in evaluated snapshots:    1
analyses in evaluated snapshots:   1
investigations evaluated:         10
specialist runs represented:      20
evidence records represented:     69
controlled failure observations:  30
```

## Metric results

| Metric | Numerator / denominator | Score | Threshold | Result |
|---|---:|---:|---:|---|
| routing_recall | 10 / 10 | 1.000 | 0.950 | PASS |
| specialist_completion | 10 / 10 | 1.000 | 0.900 | PASS |
| evidence_grounding | 10 / 10 | 1.000 | 1.000 | PASS |
| budget_compliance | 10 / 10 | 1.000 | 1.000 | PASS |
| conflict_preservation | 10 / 10 | 1.000 | 1.000 | PASS |
| final_diagnosis_grounding | 10 / 10 | 1.000 | 1.000 | PASS |
| provider_resilience | 10 / 10 | 1.000 | 0.950 | PASS |
| policy_safety | 10 / 10 | 1.000 | 1.000 | PASS |

Routing included nine investigation-required cases and one healthy case that
must not route into investigation. Persisted conflict cases retained explicit
conflict IDs and conflict counts. Evidence validation rejects unknown IDs,
malformed references, foreign investigation/server context, and missing
ownership context.

## Controlled resilience and safety

Provider tests covered valid output, retryable provider errors, malformed and
truncated JSON, empty output, HTTP 500, and timeout. Policy tests covered
unknown tools, unassigned tools, invalid arguments, write/escalation attempts,
specialist/action/round limits, and approved read-only execution.

The MCP catalog contains exactly 25 tools. No catalog description or schema
exposes raw SSH, raw SQL, arbitrary shell, `execute_command`, `database_query`,
`psql`, unbounded subprocess execution, or unrestricted filesystem writes.
Bounded non-read-only tools remain explicitly registered and policy-gated.

## Real runtime evidence

Native Claude Code 2.1.175 was invoked with Ollama model
`gemma4:e4b-it-q4_K_M`, `--permission-mode dontAsk`,
`--allowedTools mcp__vps__*`, strict project MCP configuration, and no
`--dangerously-skip-permissions`.

The latest verified session persisted:

```text
agent_job_id:       9916bb85-d310-4a8f-a6d1-bbdd7da75ea0
session_id:         496f737b-deaa-4cd5-bbaf-4f8ca55f6616
server_id:          2
report_id:          1804
analysis_id:        1635
investigation_id:   none required by persisted analysis
status:             completed
turns / tool calls: 7 / 6
MCP:                vps connected
```

The report was `connection_failed`, analysis was completed from a persisted
reuse path, and no deeper investigation was requested. This is a valid
controlled failure outcome, not a fabricated healthy result.

An earlier post-change acceptance also persisted report `1803`, analysis
`1634`, and investigation `7ff5322f-2149-454e-b2d9-8bb5d5febdcc`, exercising
the investigation-required path with 11 turns and 12 tool calls.

## Defects found and fixed

- FastAPI startup now calls the existing interrupted-job recovery hook, so
  queued/running AgentJobs cannot remain indefinitely active after restart.
- Evidence snapshots now persist investigation, server, and report ownership
  metadata. Evaluation rejects malformed, missing, foreign, or unowned context.
- Added focused C.14.12 tests for MCP exposure, malformed Claude output,
  policy/provider failures, interrupted jobs, and evidence ownership.

## Known limitations

The existing historical runtime snapshots were created before the new ownership
metadata fields were added. The evaluator uses their existing report/server
provenance where available; newly persisted snapshots contain the complete
context metadata. The real acceptance used healthy PostgreSQL/Ollama/MCP
infrastructure and did not execute remediation or a live SSH command. External
outage behavior is covered by controlled/unit failure paths, including
connection-refused evidence, bounded SSH/Claude timeouts, failed-MCP
observability, and provider timeout/error cases. The only test-suite warning is
the existing Starlette/httpx deprecation warning.

## Gate decision

C.14.12 = PASS

NEXT ALLOWED STEP:
C.14.13 — Documentation Synchronization

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
