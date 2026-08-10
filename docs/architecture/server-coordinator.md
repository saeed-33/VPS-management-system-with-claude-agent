# Server Coordinator — Phase 4.15

```text
Routing Decision
 -> Server Coordinator
 -> selected dynamic Specialists
 -> Specialist Investigation Loop (sequential in 4.15)
 -> shared investigation action budget
 -> SpecialistResults + Evidence
 -> ServerInvestigationState
```

4.15 is deliberately sequential; parallel execution belongs to 4.16.
The Coordinator composes existing Registry, Specialist Loop, Policy, Evidence,
RAG and SSH boundaries rather than duplicating them. Specialists remain
operator-defined registry data. A global investigation action budget is carried
between Specialist loops. Partial Specialist failure is isolated and successful
sibling results remain available.

Dynamic secondary Specialist spawning remains 4.17. Cross-Specialist
correlation/final diagnosis remains 4.18. Remediation remains outside Phase 4.

This boundary follows ADR-010 and the accepted Phase 4 roadmap.
