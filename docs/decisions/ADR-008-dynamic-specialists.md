# ADR-008 — Specialists Are User-Defined Runtime Data

**Status: Accepted**

## Context

Phase 4 requires specialists for domains such as CPU, memory, databases, web servers, containers, and future environment-specific technologies. Hard-coding one Python class per specialist couples product capability to application deployment and prevents operators from defining organization-specific expertise.

## Decision

Specialist definitions are user-managed persisted data.

Application code provides the generic specialist engine, contracts, registry, routing, policy, evidence, and execution infrastructure. It does not contain a closed list of specialist types.

A specialist definition may contain:

- stable slug/ID and display name.
- description and instructions.
- enabled state.
- domains/capabilities.
- trigger hints.
- Knowledge RAG topics/filters.
- allowed diagnostic tool IDs.
- priority.
- max rounds/actions.
- extensible metadata where justified.

The exact persisted schema is finalized in Step 4.2.

## Consequences

Positive:
- New PostgreSQL/Nginx/JVM/internal-service specialists do not require Python changes.
- Multiple specialists may overlap in domains.
- enable/disable and tuning are runtime operations.
- Router behavior changes through registry data.

Constraints:
- User instructions do not grant capabilities.
- Tool access is limited by registered tool IDs and policy.
- Unknown tool IDs are invalid.
- A specialist cannot invent a new executable capability.
- Definitions require validation and audit-friendly persistence.

## Rejected alternative

Hard-coded specialist classes/enums were rejected because they create deployment coupling and a closed capability catalog.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
