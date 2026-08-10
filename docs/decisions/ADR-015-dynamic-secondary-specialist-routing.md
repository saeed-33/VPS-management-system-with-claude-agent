# ADR-015: Dynamic Secondary Specialist Routing

**Status:** Accepted and runtime verified  
**Phase:** 4.17

## Context

A Specialist can determine that another enabled Specialist is better suited to follow Evidence discovered during investigation.

The reasoning contract exposes `recommended_next_specialists`, but treating model output as an execution command would violate Registry and budget boundaries.

## Decision

Model recommendations are advisory inputs to LangGraph routing.

The outer Phase 4.17 graph validates each recommendation against:

- enabled Specialist Registry membership;
- already executed Specialists;
- remaining `max_specialists`;
- remaining global `max_actions`.

Accepted recommendations form a later parallel wave using the already accepted Phase 4.16 coordinator.

The process stops when no recommendation is accepted or a budget bound is reached.

## Runtime verification

A controlled-secondary acceptance test was used to separate recommendation quality from orchestration correctness.

Only the recommendation value was injected after successful primary execution. The following remained real:

```text
primary Specialist execution
Registry lookup/validation
budget validation
duplicate suppression
secondary Specialist execution
Policy/SSH/Tool path
LangGraph dynamic-secondary runtime
```

The accepted run executed:

```text
nginx -> systemd-service
```

across two waves and passed all routing/budget/duplicate safety checks.

## Consequences

- Models cannot invent executable Specialist identities.
- Duplicate Specialist execution is suppressed.
- Secondary routing is observable in graph state.
- Later waves receive accumulated Evidence.
- Parallel execution remains isolated inside the Phase 4.16 coordinator.
- Recommendation quality can be evaluated independently from orchestration correctness.

## Provider reliability consequence

Final Synthesis may use a provider-specific compact structured output contract when required to reliably return complete JSON. This is an output-shaping concern, not a change to authorization, Evidence provenance, or Registry validation.

## Out of scope

Phase 4.17 does not correlate Specialist conclusions into a server-level diagnosis.

That is Phase 4.18.
