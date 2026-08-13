# C.14.11A.4.1 — Composition Boundary

## Goal

Move application dependency wiring out of the historical top-level
`app/bootstrap.py` module and establish `app/composition/` as the explicit
composition boundary.

## Change

`app/bootstrap.py` remains as a temporary backward-compatible facade:

```text
app.bootstrap
    -> app.composition.builder
```

The current `ApplicationContainer` and `build_container()` implementation are
moved without changing dependency construction order or runtime behavior.

## Safe migration sequence

```text
A.4.1  Establish composition package and compatibility facade
A.4.2  Split repository/service/analysis/runtime builders
A.4.3  Move interfaces/infrastructure incrementally
```

## Invariant

Composition may construct and connect components. It must not contain business
rules that belong to capabilities, policies, or infrastructure implementations.
