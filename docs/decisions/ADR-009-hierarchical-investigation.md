# ADR-009 — Hierarchical, Bounded, Read-Only Investigation

**Status: Accepted**

## Context

A server incident may span multiple domains. CPU and memory symptoms can share one process; a generic resource specialist may discover a database-specific cause. A single monolithic prompt is insufficient for controlled evidence collection and specialization.

## Decision

Phase 4 uses a hierarchy:

```text
Server Coordinator
      |
Investigation Router
      |
Specialist Tasks
      |
Specialist Investigation Loops
      |
Correlation
      |
Final Diagnosis
```

The Server Coordinator owns one server investigation and correlation. Specialists own domain-scoped tasks.

Specialists may be selected initially or dynamically in later rounds from the user-defined Specialist Registry.

Investigations are bounded by explicit budgets for specialist count, rounds, and diagnostic actions.

Independent specialists may execute concurrently when state/evidence isolation is preserved.

## Safety boundary

Phase 4 is autonomous diagnosis, not autonomous remediation.

The LLM never receives arbitrary shell execution capability. Diagnostic actions must reference registered tools with validated parameters and pass policy before execution.

Allowed direction:

```text
Specialist request
      |
Tool Registry
      |
Policy
      |
Known read-only implementation
      |
SSH/collector
      |
Evidence
```

Rejected direction:

```text
LLM -> arbitrary shell -> server
```

## Knowledge model

Specialists may receive both:

- Incident RAG: historical report/analysis cases.
- Knowledge RAG: technical documents, official documentation, internal runbooks/SOPs, known issues.

Retrieved material must preserve provenance/source identifiers.

## Consequences

- Investigation state and evidence must be traceable.
- Partial failures must not invalidate unrelated specialist work.
- Budget exhaustion is a valid terminal condition.
- Remediation requires a separate Phase 5 architecture with stronger permissions, approvals, audit, rollback, and safety controls.
