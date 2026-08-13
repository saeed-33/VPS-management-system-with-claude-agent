# C.14.11A.4.2a — Repository Composition

Repository construction is moved from `app/composition/builder.py` into
`app/composition/repositories.py`.

The new `RepositoryBundle` is composition-only. `build_container()` still
receives the same repository instances and downstream wiring is unchanged.

Next stages:
A.4.2b shared/domain services
A.4.2c analysis and investigation
A.4.2d Claude, MCP, and scheduler runtime
