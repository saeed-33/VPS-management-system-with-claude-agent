# Investigation Router

**Phase:** 4.5  
**Status:** Implemented — pending acceptance verification

## Purpose

The Investigation Router is the first decision layer that connects a
completed monitoring analysis to the dynamic Specialist Registry.

It does not run Specialists.

```text
Monitoring Report
+
Initial Analysis
+
SpecialistRegistrySnapshot
        |
InvestigationRouter
        |
InvestigationRoutingDecision
```

## Conservative first implementation

Phase 4.5 deliberately uses deterministic structural routing without an
additional LLM call.

The Router decides:

```text
should_investigate
reasons
detected_domains
selected_specialists
unmatched_issue_indexes
```

An investigation is considered actionable when at least one of these is
present:

- warning/critical analysis issue.
- warning/critical health status.
- failed/partial report or failed connection/commands.

A healthy report with no actionable issues does not open an investigation.

## Dynamic matching

The Router contains no hard-coded CPU, memory, PostgreSQL, Nginx, etc.
routing rules.

Candidate discovery comes from user-defined Specialist fields:

```text
domains
trigger_hints
priority
enabled
```

Text considered for routing comes from:

- normalized report status (for example `connection_failed` -> `connection failed`).
- analysis summary.

- actionable analysis issue title.
- issue description.
- issue evidence.
- report-level error.
- failed command name/stderr/error message.

## Scoring

Baseline structural score:

```text
trigger hint match = 5
domain match       = 2
```

If any explicit trigger-hint candidates exist, weaker domain-only
candidates are not added to the same initial decision.

If no trigger hint matches, domain-only matching is allowed as a fallback.

Candidates are sorted by:

1. score descending.
2. Specialist priority ascending.
3. name.
4. slug.
5. ID.

The router currently selects at most four Specialists. This corresponds
to the initial Investigation budget contract.

## No suitable specialist

A real problem can exist even when the user has not defined a matching
Specialist.

In that case:

```text
should_investigate = true
selected_specialists = []
reason includes no_suitable_specialist
```

The Router must never fabricate a hard-coded Specialist.

## Snapshot boundary

A single routing call uses one `SpecialistRegistrySnapshot`. This prevents
operator changes during the decision from creating an internally
inconsistent Specialist set.

## Current limitations

This baseline is lexical/structural. It does not yet:

- use an LLM for routing.
- execute Specialists.
- persist the routing decision.
- use Knowledge RAG.
- use LangGraph.
- execute diagnostics.

These later layers remain independently testable.

## Manual inspection

For an existing report that already has an analysis:

```powershell
uv run python tools/inspect_investigation_routing.py <REPORT_ID>
```

The command prints reasons, detected domains, selected Specialists and
their matched trigger/domain signals.

## Acceptance scenarios

Automated fixtures cover:

- healthy report.
- CPU issue.
- memory issue.
- CPU + memory combined.
- domain-only fallback.
- no suitable Specialist.
- connection failure.
- non-actionable info issue.
- max-specialist budget.
