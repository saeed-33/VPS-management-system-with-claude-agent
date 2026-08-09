# Diagnostic Tool Registry

**Phase:** 4.11  
**Status:** Implemented — pending acceptance

Phase 4.11 defines the diagnostic actions a Specialist may request.

It deliberately does **not** execute SSH commands yet.

```text
Specialist
   |
allowed_tool_ids
   |
DiagnosticToolRegistry
   |
typed parameter validation
   |
safe pre-defined command rendering
   |
Phase 4.12 executor
```

## Security boundary

The Specialist is never given arbitrary shell access.

A Tool contains:

```text
tool_id
name
description
domains
typed parameters
fixed command template
timeout
requires_sudo
risk
output limit
```

All Phase 4.11 tools are read-only.

Parameters are validated before rendering. Service names, paths, hosts and
ports cannot contain arbitrary shell syntax. Unknown parameters are rejected.

`shlex.join()` is used only after each dynamic value has passed the Tool's
typed validator.

## Specialist allow-list

`SpecialistRuntimeDefinition.allowed_tool_ids` already exists in the dynamic
Specialist definition.

Phase 4.11 makes it enforceable:

```text
Specialist allowed_tool_ids
      |
      +--> Tool exists?
      +--> Tool assigned?
      +--> parameters valid?
      |
      v
safe command
```

A Specialist cannot request a Registry Tool unless its exact ID appears in
`allowed_tool_ids`.

## Initial Tool set

The default registry includes read-only diagnostics for:

```text
systemd
journal
process/CPU
memory/vmstat
filesystems/inodes
network listeners/routes/connect probes
NGINX config/build information
Docker container state
PostgreSQL readiness
```

Examples:

```text
systemd-status
journal-unit
process-top-cpu
process-top-memory
memory-summary
vmstat-sample
disk-filesystems
disk-inodes
network-listeners
network-route
network-connect
nginx-config-test
docker-ps
postgres-ready
```

## Ubuntu 22.04 reference VM

The current test VM is Ubuntu Server 22.04.2. The core commands used here are
compatible with that reference environment. Optional component-specific tools
such as `nginx`, `docker`, `pg_isready`, or `nc` may be unavailable when the
corresponding package is not installed; Phase 4.12 must represent that as a
normal Tool failure, not as an Investigation crash.

## Acceptance

Inspect all tools:

```powershell
uv run python tools/inspect_diagnostic_tools.py
```

Then inspect the effective allow-list for an existing Specialist:

```powershell
uv run python tools/inspect_diagnostic_tools.py --specialist nginx
```

If the Specialist currently has no `allowed_tool_ids`, the second command
should show zero tools. That is expected until the operator assigns Tool IDs
to the Specialist definitions.

Phase 4.12 adds Tool Requests and execution through the existing bounded SSH
command executor. The Tool Registry remains the authority that turns a typed
Tool Request into command text.
