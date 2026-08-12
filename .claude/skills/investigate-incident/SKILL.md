---
name: investigate-incident
description: Coordinate a bounded investigation for one analyzed report by persisting the routing decision, running only DB-defined Specialists selected by project policy/routing, and returning evidence-grounded investigation state.
argument-hint: "<report_id> [analysis_id]"
allowed-tools:
  - mcp__vps__get_analysis
  - mcp__vps__start_investigation
  - mcp__vps__get_investigation
  - mcp__vps__get_investigation_status
  - mcp__vps__get_evidence
  - mcp__vps__get_specialist_definition
  - mcp__vps__run_specialist
---

# Investigate Incident

## Purpose

Coordinate deeper investigation only when persisted analysis identifies issues.
Specialists remain database-defined and project-authorized.

This skill does not create static CPU, Memory, database, web, or other domain
Specialists.

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
   without running a Specialist.
4. Treat `selected_specialists` as the current project authorization envelope.
   Do not run a Specialist outside that set.
5. Read the persisted investigation detail before Specialist execution so
   routing candidates, budgets, and current state are known.
6. For each selected Specialist that is still eligible:
   - call `mcp__vps__get_specialist_definition`;
   - build a concise objective only from the current analysis and persisted
     routing context;
   - call `mcp__vps__run_specialist` once.
7. `run_specialist` owns the bounded Specialist reasoning/evidence loop. Do not
   duplicate that inner loop in this skill.
8. If one Specialist fails with a Specialist-local controlled failure, preserve
   the failure and continue with other authorized selected Specialists when the
   investigation remains valid.
9. After Specialist execution, read:
   - `mcp__vps__get_investigation_status`;
   - `mcp__vps__get_evidence`;
   - `mcp__vps__get_investigation`.
10. If `final_diagnosis_available == false`, return
    `investigation_incomplete`. Do not fabricate a final diagnosis.
11. If final diagnosis is persisted, summarize only persisted findings,
    conflicts, claims, and Evidence references.

## Current selection boundary

C.14.2 does not pretend Claude has already replaced every Python routing
decision.

At this stage:

```text
project start_investigation
  -> persists routing decision
  -> returns selected Specialists

Claude
  -> owns bounded execution order/objectives inside that authorized set
```

The remaining duplicated orchestration/routing ownership is addressed in later
C.14 steps after the real Claude session path exists and passes parity tests.

## Concurrency rule

Default to sequential Specialist tool calls in C.14.2.

Do not assume parallel writes to persisted investigation state are safe until
the C.14 runtime concurrency tests explicitly prove isolation.

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
specialist budget/policy/tool denial
provider/tool failure inside one Specialist
```

Never bypass a denial by requesting a raw shell/SSH/SQL path.

## Stopping conditions

Stop when:

```text
no investigation is required
no authorized selected Specialist remains
project budget/policy prevents further work
all selected Specialists have returned/failed
a final diagnosis is persisted
the investigation is persistently incomplete and no authorized next action exists
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

All IDs must come from project tool results.
