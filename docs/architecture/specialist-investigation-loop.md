# Specialist Investigation Loop

**Phase:** 4.14  
**Status:** Implemented — pending runtime acceptance

## Purpose

Phase 4.14 closes the single-Specialist diagnostic loop.

```text
Build bounded context
    |
    v
Specialist reasoning
    |
    +-- enough evidence -> final result
    |
    `-- diagnostic_tool_requests
              |
              v
        Diagnostic Policy
              |
        +-----+------+
        |            |
      DENY          ALLOW
        |            |
        |            v
        |      Evidence Collection
        |            |
        +------------+
              |
              v
        rebuild context
              |
              v
          reason again
```

The loop is bounded by both the Specialist definition and the Investigation
budget.

## Structured Tool Requests

`missing_evidence` remains a human-readable diagnostic field.

It is **not** parsed into commands.

The reasoning schema now includes:

```json
{
  "diagnostic_tool_requests": [
    {
      "tool_id": "systemd-status",
      "arguments": {
        "service": "nginx"
      },
      "rationale": "Need the current service state."
    }
  ]
}
```

The LLM never returns shell command text.

## Tool Catalog

Before each reasoning call, the loop supplies only the Diagnostic Tools
assigned to the current Specialist.

The catalog contains:

```text
tool_id
name
description
domains
typed parameter schema
```

It does not expose command templates.

The model may request only catalog IDs, but the model output is still
untrusted. Phase 4.12 remains the authoritative policy gate.

## Round semantics

A round means one Specialist reasoning pass.

After evidence is collected, a new round is required to consume that evidence.

Therefore, if the model asks for additional Tools on the final available
round, those requests are not executed.

This prevents:

```text
collect evidence
-> no budget left to reason about it
```

## Action semantics

Only actual allowed SSH executions consume action budget.

```text
Policy DENY     -> 0 actions
duplicate skip  -> 0 actions
SSH execution   -> +1 action
```

Both limits apply:

```text
Specialist.max_actions
InvestigationBudget.max_actions
```

## Duplicate suppression

An identical `(tool_id, canonical arguments)` request is executed at most once
inside a Specialist task.

If the LLM requests the same diagnostic again without changing arguments, the
loop records:

```text
duplicate_request
```

and does not spend another SSH action.

This protects against repetitive LLM loops.

## Stop reasons

```text
completed
max_rounds
max_actions
no_evidence_collected
```

`no_evidence_collected` includes cases where all requested Tools are denied or
duplicates, making another identical reasoning round unproductive.

## Evidence propagation

Every collected EvidenceReference is fed into the next
`SpecialistContextBuilder.build()` call.

The round-specific task expands its `evidence_ids` so newly collected Evidence
is not filtered out by the existing task-level evidence allow-list.

## Traceability

Every round records:

```text
round number
confidence
requested Tool IDs
per-Tool policy/execution decision
denial/skip reasons
collected evidence IDs
```

The Phase 4.14 result is in-memory. Investigation persistence integration is
handled by later orchestration/productization phases.

## Safety

The loop cannot execute raw shell.

```text
LLM structured Tool request
-> Tool Registry
-> Diagnostic Policy
-> approved execution envelope
-> Evidence Collection
```

The existing 4.12 and 4.13 boundaries remain mandatory.

## Runtime acceptance

Use a reachable managed Ubuntu server and a Specialist with useful assigned
Tools.

Example:

```powershell
uv run python tools/run_specialist_investigation.py `
  2 `
  nginx `
  "Determine whether NGINX is installed/running and what live evidence supports the conclusion." `
  --domains nginx,http,network `
  --max-rounds 3 `
  --max-actions 5
```

Expected behavior:

```text
Round 1:
  low confidence
  requests one or more allowed Tools

SSH Evidence is collected.

Round 2/3:
  context contains new Evidence
  confidence/conclusion changes
  loop terminates safely
```

A correct result on a server without NGINX may conclude that the service is
not installed/present, citing the `systemd-status` Evidence, rather than
treating exit status 4 as an orchestration failure.

## Next

Phase 4.15 — Server Coordinator will run selected Specialists under one
server-level Investigation state and global budgets.

## Objective discipline and synthesis fallback

The Specialist Objective is authoritative. The reasoning model must not
reinterpret it as a different incident category merely because broad Tools are
available.

If a reasoning round requests only denied or duplicate Tools and therefore
collects no new Evidence, the loop does not immediately return that procedural
response as the final diagnosis. When another round remains, the next round is
forced into synthesis-only mode with no Diagnostic Tool catalog.

This prevents duplicate-request loops from terminating with text such as
"I will now check..." instead of an evidence-grounded conclusion.
