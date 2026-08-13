# Specialist Registry Service

**Phase:** 4.4  
**Status:** Implemented — pending test/runtime verification

`SpecialistRegistry` is the runtime boundary between persisted
`specialist_definitions` and the Investigation Router that will be built
in Phase 4.5.

```text
specialist_definitions
        |
SpecialistDefinitionRepository
        |
SpecialistRegistry
        |
SpecialistRegistrySnapshot
        |
Investigation Router
```

The registry reads enabled definitions only. Disabled specialists remain
stored and editable but cannot enter a runtime snapshot.

SQLAlchemy models are converted to immutable
`SpecialistRuntimeDefinition` values. Domains are normalized
case-insensitively and malformed enabled definitions fail explicitly.

`registry.snapshot()` performs one repository read and returns a stable
view. This allows one future routing decision to use a coherent set of
definitions even if an operator changes the UI during that decision. A
new snapshot observes the new database state.

Supported lookups:

```text
get_by_slug(slug)
find_by_domain(domain)
find_by_domains(domains, require_all=False)
```

Multi-domain lookup is deterministic: matched-domain count descending,
then priority ascending, then name, slug and ID. This is structural
matching only; Phase 4.5 owns the actual routing decision.

`allowed_tool_ids` are preserved but not validated against executable
tools yet. Diagnostic Tool Registry arrives in Phase 4.11, so 4.4 grants
no execution capability.

Manual inspection:

```powershell
uv run python tools/dev/inspect_specialist_registry.py
uv run python tools/dev/inspect_specialist_registry.py --domain cpu
uv run python tools/dev/inspect_specialist_registry.py --domains cpu,process
uv run python tools/dev/inspect_specialist_registry.py --domains cpu,process --require-all
```

Acceptance:

```powershell
uv run python -m pytest
uv run python tools/dev/inspect_specialist_registry.py
uv run python tools/dev/inspect_specialist_registry.py --domain cpu
```

No database migration, LLM, Claude-supervised, SSH or investigation execution is
introduced in 4.4.

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
