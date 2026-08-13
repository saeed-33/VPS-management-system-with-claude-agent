# Diagnostic Tool Registry

The Diagnostic Tool Registry is the Python-owned boundary for Specialist
diagnostic requests. It is implemented and covered by architecture, policy,
and runtime acceptance tests.

```text
Specialist allowed_tool_ids
        |
registered DiagnosticToolRegistry
        |
typed argument validation
        |
DiagnosticPolicyEngine
        |
known-hosts SSH executor
        |
EvidenceReference
```

## Security boundary

Specialists and Claude never receive arbitrary shell access. A registered Tool
contains a stable ID, typed parameters, a fixed command template, timeout,
risk, and output limit. Unknown tools, unknown parameters, invalid arguments,
unassigned Specialist tools, policy denials, and budget exhaustion fail closed.

Only bounded read-only diagnostic commands are available in the current Phase C
runtime. SSH uses the configured private key and `known_hosts`; command text is
rendered only after typed validation. Denials do not expose executable commands.

## Dynamic Specialist allow-list

`SpecialistRuntimeDefinition.allowed_tool_ids` is loaded from the database and
validated against the registered Tool catalog. A Specialist cannot request a
Tool unless its exact ID is present in its persisted allow-list.

## Current tool families

The registry covers bounded diagnostics for systemd/journal, processes and
memory, filesystems, network state, NGINX, Docker, and PostgreSQL readiness.
The public Claude-facing MCP catalog remains a separate bounded surface and
does not expose raw SSH or arbitrary command execution.

## Verification

```powershell
uv run python tools/dev/inspect_diagnostic_tools.py
uv run python tools/dev/inspect_diagnostic_policy.py
uv run python -m pytest tests/test_diagnostic_tool_registry.py tests/test_diagnostic_policy.py -v
```

The C.14.12 readiness gate accepted policy safety and provider/runtime failure
handling. Production remediation is not authorized.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
