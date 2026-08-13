# C.14.11A.4.3d — Database Models and Migrations Boundary

SQLAlchemy model implementations now live under:

`app/infrastructure/database/models/`

Historical Python model modules remain thin compatibility facades during A.4.

SQL migration assets are copied byte-for-byte to:

`app/infrastructure/database/migrations/`

The historical SQL files remain temporarily as a compatibility mirror because
plain SQL files cannot re-export another path. The migration verifies that both
trees are byte-identical.

Production Python imports are migrated from
`app.shared.database.models` to `app.infrastructure.database.models`.

This is a package-boundary change only. It does not alter table names, columns,
relationships, constraints, migration SQL, or database runtime behavior.
