# ADR-015: Dynamic Secondary Specialist Routing

**Status:** Accepted  
**Phase:** 4.17

## Context

A Specialist can identify that another enabled Specialist is better suited to
follow evidence discovered during investigation. The reasoning contract already
contains `recommended_next_specialists`.

Treating those recommendations as direct execution commands would violate the
Registry and Investigation budget boundaries.

## Decision

Model recommendations are advisory inputs to LangGraph routing.

The Phase 4.17 outer graph validates recommendations against:

- enabled Specialist Registry membership;
- already executed Specialists;
- remaining `max_specialists`;
- remaining `max_actions`.

Accepted recommendations form another parallel wave through the Phase 4.16
LangGraph coordinator.

The process may repeat until no recommendation is accepted or a budget bound is
reached.

## Consequences

- Models cannot invent executable Specialist identities.
- Duplicate Specialist execution is suppressed.
- Follow-up routing is visible in graph state and final metadata.
- Evidence from earlier waves is available to later Specialists.
- Parallel behavior remains isolated inside the already accepted Phase 4.16
  coordinator.

## Out of scope

Phase 4.17 does not correlate Specialist conclusions or produce a new global
diagnosis. That remains Phase 4.18.
