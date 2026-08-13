# C.14.11A.4.3d — Database Models and Migrations Boundary

> Historical migration record. A.9 removed the temporary compatibility mirror;
> only the infrastructure paths below remain active.

SQLAlchemy model implementations now live under:

`app/infrastructure/database/models/`

SQL migration assets are canonical under:

`app/infrastructure/database/migrations/`

There is no second shared migration tree. Production and test imports use the
infrastructure database package.

This is a package-boundary change only. It does not alter table names, columns,
relationships, constraints, migration SQL, or database runtime behavior.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
