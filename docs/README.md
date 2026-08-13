# Documentation Guide

<!-- DOC-STATUS: CURRENT -->

This directory contains the current operating truth, accepted decisions, and
historical milestone records for AI VPS Management.

## Canonical current documents

- [Project status](PROJECT_STATUS.md) — one current gate/status source of truth.
- [Project structure](PROJECT_STRUCTURE.md) — generated inventory of the actual
  checkout.
- [Architecture overview](architecture/overview.md) — current runtime and
  responsibility boundary.
- [Current workflows](workflows/current-workflows.md) — operational sequence.
- [Testing strategy](testing/TESTING_STRATEGY.md) — test layers and acceptance
  requirements.
- [Runtime configuration](operations/configuration.md) — active settings and
  prerequisites.
- [Running the project](operations/running-project.md) — startup and health
  checks.
- [Claude runtime](operations/claude-runtime.md) — Claude/Ollama/MCP contract.
- [C.14.12 readiness closeout](architecture/c14-12-runtime-readiness-gate.md)
  — accepted readiness evidence.

## Supporting documents

- `docs/testing/` contains unit, integration, controlled-evaluation, and
  real-runtime testing references.
- `docs/operations/` contains configuration, database, startup, and runtime
  procedures.
- `docs/architecture/` contains current subsystem references and historical
  C.14 migration records.
- `docs/decisions/` contains accepted ADRs. ADRs are preserved decisions and
  may describe the state that existed when they were accepted.
- `docs/roadmap/` contains roadmap, phase, and closeout records. Historical
  milestone records are not current operator instructions.

## Current status at a glance

```text
Phase 4.20: COMPLETE
C.14.0-C.14.11: COMPLETE
C.14.11A: PASS
C.14.12: PASS
C.14.13: PASS
C.14.14: PASS
Phase C: COMPLETE / CLOSED
Phase 5: NEXT
automatic_remediation_allowed: false
```

For the generated classification of every Markdown document, see
[DOCUMENTATION_INVENTORY.md](DOCUMENTATION_INVENTORY.md).

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
