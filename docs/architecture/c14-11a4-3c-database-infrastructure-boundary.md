# C.14.11A.4.3c — Database Infrastructure Boundary

> Historical migration record. A.9 removed the temporary `app/shared/database`
> compatibility layer after all production, test, and tooling imports moved to
> `app/infrastructure/database`.

This migration moves database runtime implementation into:

- `app/infrastructure/database/base.py`
- `app/infrastructure/database/engine.py`
- `app/infrastructure/database/session.py`
- `app/infrastructure/database/repositories/*.py`

The database implementation, models, repositories, session, and migrations
now have one owner under `app/infrastructure/database/`. The database schema
and migration SQL were preserved unchanged.
