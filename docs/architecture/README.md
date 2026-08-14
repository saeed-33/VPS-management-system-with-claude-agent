# Current Architecture

<!-- DOC-STATUS: CURRENT_CANONICAL -->

The current architecture is defined by [`system-overview.md`](system-overview.md),
[`component-architecture.md`](component-architecture.md), and the focused
documents below. It is not organized as a phase sequence.

- [System overview](system-overview.md)
- [Component and dependency architecture](component-architecture.md)
- [Claude/Ollama/MCP runtime](agent-runtime-architecture.md)
- [Capability architecture](capability-architecture.md)
- [Security, policy, and audit architecture](security-architecture.md)
- [Data and database architecture](data-architecture.md)
- [Admin UI architecture](admin-ui-architecture.md)
- [Deployment architecture](deployment-architecture.md)
- [Editable diagrams](diagrams/README.md)

The source of truth for package names is the local `app/` tree. The source of
truth for persistence is `tools/bootstrap_database.py`, SQL migrations, and
the SQLAlchemy models. The source of truth for MCP is
`app/interfaces/mcp/catalog.py` and `ProjectMcpToolBoundary.list_tools()`.

## Current safety invariant

```text
Claude Code decides WHAT / NEXT.
Python decides WHETHER ALLOWED and HOW EXECUTED SAFELY.
```

Claude is supervisory. It cannot create policies, bypass sandbox or approval,
inject issue fingerprints, issue raw SSH/SQL/shell, or alter the global
automatic-remediation switch. Python and PostgreSQL own policy gates,
Evidence, authorization, reservations, execution, verification, rollback,
and audit.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
