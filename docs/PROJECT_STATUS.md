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
Phase 5: COMPLETE / CLOSED
Phase 5 readiness: 13/13 PASS
Phase 6: IMPLEMENTED / NOT CLOSED
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
readiness: BLOCKED_BY_SANDBOX_RUNTIME
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
- Phase 5 supervised remediation contracts, additive persistence, named write
  registry, approval fingerprinting, controlled execution, verification,
  rollback, audit events, Admin API/UI, and Claude workflow integration.

- Phase 5 real supervised remediation acceptance: PASS on the explicitly
  designated non-production `phase5-lab` target (server 4).
- Final Phase 5 regression: `433 passed, 2 skipped, 1 warning`.
- Phase 6 adds a fingerprint-bound isolated validation record and approval
  gate. The native-sandbox runtime requires explicit attestation from WSL2;
  no unsandboxed fallback is permitted.


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

Phase 5 Supervised Remediation is complete and closed. The deterministic
readiness matrix is 13/13 PASS, including real supervised remediation
acceptance against the explicitly designated non-production `phase5-lab`
target (server 4). The accepted flow persisted Evidence, human approval,
controlled execution, verification, idempotency, state-aware rollback, and
audit events, and restored the dedicated service to its original `inactive`
state. Automatic remediation remains disabled.

Phase 6 Claude-Native Isolated Sandbox Validation is implemented but not
closed. The deterministic 13-dimension gate is blocked until a real native
sandbox runtime attestation and safe validation acceptance are available.

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
