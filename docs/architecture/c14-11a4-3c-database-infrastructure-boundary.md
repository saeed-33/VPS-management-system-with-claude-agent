# C.14.11A.4.3c — Database Infrastructure Boundary

This migration moves database runtime implementation into:

- `app/infrastructure/database/base.py`
- `app/infrastructure/database/engine.py`
- `app/infrastructure/database/session.py`
- `app/infrastructure/database/repositories/*.py`

Historical `app/shared/database` paths remain compatibility facades during A.4.

This step deliberately does not move:

- `app/shared/database/models/`
- `app/shared/database/migrations/`

Those are deferred so the SQLAlchemy schema/migration surface is not changed
in the same operation as repository wiring.

Production imports under `app/` are migrated to Infrastructure paths for
base/engine/session/repositories. Tests and tools may continue using the old
paths through compatibility facades until A.4.6.
