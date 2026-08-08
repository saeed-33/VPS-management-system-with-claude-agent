# Current Workflows

## Monitoring

```text
Load server
 -> validate monitor_enabled/profile
 -> load enabled commands
 -> SSH
 -> execute commands
 -> build/save report
 -> enqueue analysis
```

## Analysis

```text
Report
 -> normalize + fingerprint
 -> exact match? -> REUSE
 -> otherwise Hybrid Retrieval
 -> accepted context? -> ASSISTED
 -> none? -> FULL
 -> LLM for ASSISTED/FULL
 -> save/index/metrics
```

## Specialist Management

```text
Operator
 -> /specialists UI or /api/specialists
 -> SpecialistDefinitionService
 -> SpecialistDefinitionRepository
 -> specialist_definitions
```

## Specialist Registry

```text
specialist_definitions
 -> list_enabled()
 -> SpecialistRegistry
 -> validate + normalize
 -> SpecialistRegistrySnapshot
 -> domain lookup
```

A snapshot contains enabled Specialists only, is stable after creation, and supports lookup by slug, one domain, or multiple domains.

Multi-domain matching orders by matched-domain count descending, then priority ascending, then name/slug/id.

This is candidate discovery only. Phase 4.5 will own the actual investigation routing decision.

## Next workflow boundary

```text
Current report
+
Initial analysis
+
SpecialistRegistrySnapshot
 -> Investigation Router
 -> Should investigate?
 -> Detected domains
 -> Selected Specialists
```

No Specialist LLM, diagnostic execution, or LangGraph loop exists yet.

## Investigation Routing — Phase 4.5

```text
Monitoring Report
+
Initial Analysis
+
SpecialistRegistrySnapshot
 -> InvestigationRouter
 -> should_investigate
 -> detected domains
 -> selected Specialists
```

The first Router implementation is deterministic and conservative. It uses
user-defined `domains` and `trigger_hints`; it does not hard-code CPU,
Memory, PostgreSQL or other Specialist types and does not invoke another LLM.

