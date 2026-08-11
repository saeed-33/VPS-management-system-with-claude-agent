# Specialist Investigation Loop

**Phase:** 4.14  
**Status:** Implemented and runtime accepted

## Purpose

Phase 4.14 closes the bounded single-Specialist diagnostic loop.

```text
Build bounded context
    |
Specialist reasoning
    |
    +-- enough evidence -> final result
    |
    `-- diagnostic_tool_requests
              |
        Diagnostic Policy
              |
        +-----+------+
        |            |
      DENY          ALLOW
        |            |
        |      Evidence Collection
        |            |
        +------------+
              |
        rebuild context
              |
          reason again
```

## Structured Tool Requests

`missing_evidence` is human-readable diagnostic output. It is not parsed into shell commands.

The model may request only registered Tool IDs and typed arguments.

Command templates are never exposed to the model.

## Round semantics

A round is one Specialist reasoning pass.

After Evidence is collected, another reasoning pass is required to consume it.

If Tool requests occur on the final available round, they are not executed because there would be no remaining round to reason about the result.

## Action semantics

Only actual allowed SSH executions consume action budget.

```text
Policy DENY     -> 0 actions
duplicate skip  -> 0 actions
SSH execution   -> +1 action
```

Both Specialist and Investigation limits apply.

## Duplicate suppression

An identical `(tool_id, canonical arguments)` request executes at most once inside a Specialist task.

Repeated requests are recorded as:

```text
duplicate_request
```

without another SSH action.

## Stop reasons

```text
completed
max_rounds
max_actions
no_evidence_collected
```

## Evidence propagation

Every collected `EvidenceReference` is fed into the next `SpecialistContextBuilder.build()` call.

Provenance IDs remain validated against the actual bounded context.

## Objective discipline and synthesis fallback

The Specialist objective is authoritative.

If a round requests only denied or duplicate Tools and collects no new Evidence, the loop can enter synthesis-only mode rather than returning procedural text as the final result.

For the accepted Ollama runtime, Final Synthesis uses a compact output contract:

```text
summary
confidence
missing_evidence
recommended_next_specialists
```

Normal reasoning retains the richer findings/hypotheses/ruled-out/provenance/Tool-request contract.

## Runtime integration through Phase 4.17

The accepted loop is now used by:

```text
Phase 4.15 Server Coordinator
Phase 4.16 LangGraph parallel workers
Phase 4.17 dynamic secondary Specialist waves
```

Each worker receives bounded budgets. No orchestration layer may bypass the Tool Registry, Policy Engine, or Evidence Collection boundary.

Phase 4.14 is closed and runtime accepted.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
