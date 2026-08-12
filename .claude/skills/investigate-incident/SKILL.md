---
name: investigate-incident
description: Coordinate a bounded investigation for one analyzed report by persisting the routing decision and delegating only project-selected DB Specialist tasks to specialist-worker.
argument-hint: "<report_id> [analysis_id]"
allowed-tools:
  - mcp__vps__get_analysis
  - mcp__vps__start_investigation
  - mcp__vps__get_investigation
  - mcp__vps__get_investigation_status
  - mcp__vps__get_evidence
  - Agent(specialist-worker)
---

# Investigate Incident

## Purpose

Coordinate deeper investigation only when persisted analysis identifies issues.

Specialists remain database-defined and project-authorized. This skill runs in
the main per-server supervisor context and delegates selected Specialist work to
the bounded `specialist-worker`.

## Input contract

Required:

```text
report_id: positive integer
```

Optional:

```text
analysis_id: positive integer
```

## Preconditions

1. Read the persisted analysis using `analysis_id` when supplied, otherwise
   `report_id`.
2. Stop if analysis is unavailable.
3. If the persisted analysis contains no issues requiring investigation, return
   `no_investigation_needed` and do not create an investigation.

Do not infer an issue solely from historical Knowledge/RAG context.

## Workflow

1. Call `mcp__vps__start_investigation` with `report_id` and the verified
   `analysis_id` when available.
2. Read `routing.should_investigate`,
   `routing.selected_specialists`, and the persisted investigation.
3. If `should_investigate == false`, return the persisted investigation state
   without delegating a Specialist.
4. Treat `selected_specialists` as the current project authorization envelope.
5. Read the persisted investigation detail/status before delegation.
6. For each selected Specialist still eligible:
   - delegate to `Agent(specialist-worker)`;
   - pass `investigation_id`, selected `specialist_slug`, and a concise
     evidence-grounded objective;
   - do not pass credentials or raw commands.
7. The worker verifies the DB definition and invokes the current bounded project
   Specialist capability.
8. If one worker returns a Specialist-local controlled failure, preserve it and
   continue only when the persisted investigation remains valid and another
   selected Specialist is still authorized.
9. After delegation, read:
   - `mcp__vps__get_investigation_status`;
   - `mcp__vps__get_evidence`;
   - `mcp__vps__get_investigation`.
10. If `final_diagnosis_available == false`, return
    `investigation_incomplete`. Do not fabricate a final diagnosis.
11. If final diagnosis is persisted, summarize only persisted findings,
    conflicts, claims, and Evidence references.

## Current selection boundary

The project `start_investigation` tool currently persists the routing decision
and selected Specialist set.

Claude owns the bounded delegation order/objectives inside that authorized set.

Later C.14 steps may move more high-level selection/sequencing out of Python
after the real Claude runtime and parity tests are available.

## Concurrency rule

Default to sequential Specialist delegation in the current transition.

Do not assume concurrent writes to one persisted investigation are safe until
C.14 runtime concurrency tests prove isolation.

## Failure behavior

Fatal investigation failures:

```text
analysis_not_found
investigation_not_found
invalid persisted routing state
```

Specialist-local controlled failures may be isolated:

```text
specialist_not_found
specialist_not_selected
budget/policy denial
provider/tool failure inside one Specialist
```

Never bypass a denial through shell/SSH/SQL.

## Stopping conditions

Stop when:

```text
no investigation is required
no authorized selected Specialist remains
project budget/policy prevents further work
all delegated selected Specialists have returned/failed
a final diagnosis is persisted
the investigation is incomplete and no authorized next action exists
```

## Output contract

Return:

```text
status
investigation_id
report_id
analysis_id
selected_specialists
completed_specialists
failed_specialists
evidence_ids
final_diagnosis_available
remaining_uncertainty
error_code/error_message, when failed
```

All IDs must come from project tools or delegated worker results.
