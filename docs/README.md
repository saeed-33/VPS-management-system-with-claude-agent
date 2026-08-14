# Documentation Map

<!-- DOC-STATUS: CURRENT_CANONICAL -->

This is the canonical map for the current implementation. Source code and
tests are authoritative over prose. Current architecture describes what the
system is now; `docs/process/` and historical ADR/roadmap records describe how
it got there.

## Current sources of truth

| Area | Current document | Purpose and audience |
|---|---|---|
| Project status | [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | Gate state for maintainers, reviewers, and operators. |
| Architecture | [`architecture/README.md`](architecture/README.md) | Current system boundaries and component responsibilities. |
| Requirements | [`requirements/README.md`](requirements/README.md) | Functional, non-functional, and specification traceability. |
| Use cases | [`use-cases/README.md`](use-cases/README.md) | Actor-oriented behavior and permissions. |
| Workflows | [`workflows/README.md`](workflows/README.md) | Operational lifecycle flows and fail-closed branches. |
| Testing strategy | [`testing/README.md`](testing/README.md) | Test layers, environments, and methods. |
| Test results | [`testing/test-results.md`](testing/test-results.md) | Latest verifiable non-real results and infrastructure checks. |
| Implementation history | [`process/implementation-history.md`](process/implementation-history.md) | Phase/milestone history kept separate from architecture. |
| Future work | [`roadmap/future-work.md`](roadmap/future-work.md) | Deferred requirements and post-v1 work. |
| Technical report | [`report/README.md`](report/README.md) | Arabic DOCX scope, provenance, and validation. |

## Supporting documentation

- `docs/operations/` contains startup, configuration, deployment, database,
  Admin, and runtime runbooks.
- `docs/api/` contains endpoint-oriented reference material.
- `docs/security/` contains security boundaries and negative guarantees.
- `docs/decisions/` contains accepted ADRs. ADRs are historical decisions,
  not replacements for the current architecture document.
- `docs/roadmap/` contains preserved milestone records and the current
  deferred plan. Files named `phase-*`, `*-implementation-plan.md`, and
  `*-final-report.md` are historical unless explicitly linked from the
  canonical map.
- `docs/architecture/steps/` contains preserved implementation notes. These
  are historical closeout records where they describe a completed phase; they
  must not be read as the current component map.

## Current verified baseline

As verified on 2026-08-14 in the stable WSL environment:

```text
Python: 3.14.7
Non-real suite: 586 passed, 1 warning
Database: 33/33 tables, pgvector OK, 3/3 custom RAG indexes
MCP catalog: 25 tools
Routes: 99 total / 73 OpenAPI / 26 web-only
Automatic remediation: false by default
```

The repository contains a contradiction for Phase 6 live acceptance: the
machine-readable readiness artifact says `PASS`, while the Phase 6 final
report and default real test path say `BLOCKED_BY_SANDBOX_RUNTIME`. Phase 7
implementation is present, but no standalone live acceptance result is stored
in the repository. This is explicitly tracked in
[`roadmap/deferred-requirements.md`](roadmap/deferred-requirements.md).

## Obsolete or historical claims

Older documents may mention earlier MCP counts, phase gates, or proposed
components. They remain for historical traceability and are classified in
[`DOCUMENTATION_INVENTORY.md`](DOCUMENTATION_INVENTORY.md). They do not
override the current map, source code, tests, or current test-results record.

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
