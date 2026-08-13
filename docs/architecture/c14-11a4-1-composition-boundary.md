# C.14.11A.4.1 — Composition Boundary

> Historical migration record. C.14.11A structural closure superseded the
> temporary facade described by this step; `app/bootstrap.py` has now been
> removed.

## Goal

Move application dependency wiring into the explicit `app/composition/`
boundary. The canonical container is exported by `app.composition` and all
application/tools consumers import it from there.

## Historical transition

The former transition state exposed `app.bootstrap` as a compatibility facade
over `app.composition.builder`. That facade was intentionally removed after
all consumers were migrated.

## Invariant

Composition constructs and connects components. It does not contain business
rules that belong to capabilities, policies, or infrastructure implementations.
