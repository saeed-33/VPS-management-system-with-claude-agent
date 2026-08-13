# Current Project Status

<!-- DOC-STATUS: CURRENT -->

This is the canonical current-state status document. Historical ADRs and
milestone records remain available in `docs/decisions/`, `docs/architecture/`,
and `docs/roadmap/` but do not override this status.

## Gate state

```text
Phase 4.20: COMPLETE
C.14.0-C.14.11: COMPLETE
C.14.11A: PASS
C.14.12: PASS
C.14.13: PASS
C.14.14: PASS
Phase C: COMPLETE / CLOSED
Phase 5: NEXT
automatic_remediation_allowed: false
readiness: ready_for_supervised_operations
```

### State meanings

| State | Meaning |
|---|---|
| IMPLEMENTED | Present in the repository and covered by normal tests. |
| ACCEPTED | Passed its defined gate, including required evidence. |
| PENDING | The next authorized gate; not yet closed. |
| NOT AUTHORIZED | Explicitly outside the current operational boundary. |

## Implemented and accepted

- Phase 4.20 evaluation, safety, and production-readiness gate.
- C.14.0-C.14.11 Claude-native runtime milestones.
- C.14.11A canonical package consolidation and legacy-tree removal.
- Native Claude Code supervisory runtime using Ollama.
- Bounded `vps` MCP server with 24 project tools.
- PostgreSQL persistence for reports, analyses, investigations, evidence, and
  AgentJob/session observability.
- DB-defined Specialist routing and bounded investigation execution.
- Policy, budgets, known-hosts SSH safety, and fail-closed Evidence grounding.
- R.5 Documentation and Tests: complete.

## C.14.12 readiness acceptance

The accepted dataset contains 11 runtime sessions, 50 persisted runtime
observations, 30 controlled observations, and 80 aggregate observations. The
accepted real runtime used job `9916bb85-d310-4a8f-a6d1-bbdd7da75ea0`, session
`496f737b-deaa-4cd5-bbaf-4f8ca55f6616`, server 2, report 1804, analysis 1635,
model `gemma4:e4b-it-q4_K_M`, and connected `vps` MCP. Its connection-failure
outcome was correctly persisted as a controlled failure.

| Dimension | Result | Threshold |
|---|---:|---:|
| routing_recall | 10/10, 1.000 PASS | 0.950 |
| specialist_completion | 10/10, 1.000 PASS | 0.900 |
| evidence_grounding | 10/10, 1.000 PASS | 1.000 |
| budget_compliance | 10/10, 1.000 PASS | 1.000 |
| conflict_preservation | 10/10, 1.000 PASS | 1.000 |
| final_diagnosis_grounding | 10/10, 1.000 PASS | 1.000 |
| provider_resilience | 10/10, 1.000 PASS | 0.950 |
| policy_safety | 10/10, 1.000 PASS | 1.000 |

Overall: **8/8 readiness dimensions PASS**.

## Current architecture boundary

```text
Claude Code = supervisory reasoning and sequencing
Ollama      = operational LLM provider
MCP         = bounded Claude-facing capability surface
Python      = execution, validation, policy, evidence, persistence, budgets,
              SSH safety, database access, and Admin/API
```

Claude decides WHAT/NEXT. Python decides WHETHER ALLOWED and HOW EXECUTED
SAFELY. No active OpenAI or LangGraph runtime exists.

## Pending and not authorized

C.14.14 is accepted. Implementation, architecture, safety, tests, runtime
evidence, and documentation agree. Phase C is closed.

Phase 5 Supervised Remediation is the next allowed phase, but it has not
started. Automatic restart, process termination, package changes, configuration
writes, reboot, firewall changes, arbitrary shell, and production remediation
remain unauthorized until Phase 5 explicitly adds and accepts those contracts.

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
