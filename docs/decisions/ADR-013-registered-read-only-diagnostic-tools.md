# ADR-013 — Specialists Use Registered Read-Only Diagnostic Tools, Never Arbitrary Shell

**Status:** Accepted  
**Phase:** 4.11 onward

## Decision

Phase 4 Specialists may only request diagnostic capabilities registered in a
project-owned `DiagnosticToolRegistry`.

They are never given arbitrary shell access.

```text
Specialist
   |
allowed_tool_ids
   |
Tool Request
   |
Diagnostic Policy / Registry
   |
typed parameter validation
   |
fixed command rendering
   |
bounded SSH executor
```

## Tool definition

A registered tool declares:

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

The current Phase 4 risk class is:

```text
read_only
```

## Parameter safety

Dynamic values are typed and validated before command rendering.

Examples:

```text
service
host
port
absolute path
integer limits
safe token
```

Unknown arguments are rejected.

Values such as:

```text
nginx; rm -rf /
```

must never become command text.

## Specialist permissions

Dynamic Specialist definitions already contain:

```text
allowed_tool_ids
```

This field is the capability allow-list.

A Tool Request is valid only if:

```text
tool exists
AND tool ID is assigned to the Specialist
AND parameters validate
AND policy/budget allows it
```

The Registry therefore provides capability definitions; it does not grant
permissions by itself.

## Initial tool inventory

The accepted 4.11 registry contains 18 read-only tools covering:

```text
systemd / journal
CPU / process
memory / vmstat
filesystem / inode
network listeners / sockets / routes / TCP probes
NGINX validation/build information
Docker container state
PostgreSQL readiness
```

Examples:

```text
systemd-status
systemd-failed
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
nginx-version
docker-ps
postgres-ready
```

## Execution boundary

4.11 only defines and validates Tools.

The existing project SSH implementation remains responsible for transport.
Tool execution must reuse that bounded implementation rather than introduce a
second SSH stack.

Policy and Evidence Collection are separate subsequent steps.

## Reference test environment

The current controlled Linux test target is:

```text
Ubuntu Server 22.04.2 amd64 on VMware
```

Component-specific commands may legitimately be absent when their packages
are not installed. That condition is a Tool result/failure, not a reason to
fall back to arbitrary shell.

## Consequences

- The LLM chooses capabilities, not shell syntax.
- Security review can reason about a finite Tool inventory.
- Tool permissions are user-controlled through dynamic Specialist data.
- Execution timeouts/output budgets are enforceable.
- Phase 5 remediation can later use a separate risk/approval model rather than
  silently expanding Phase 4 privileges.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
