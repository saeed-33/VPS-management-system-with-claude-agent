# Evidence Collection

**Phase:** 4.13  
**Status:** Implemented — pending runtime acceptance

Phase 4.13 is the first investigation step that performs a real diagnostic
action on a target server.

```text
DiagnosticToolCall
    -> Diagnostic Policy Engine
    -> DENY: stop, no SSH
    -> ALLOW
    -> EvidenceCollectionService
    -> existing SSHClient + SSHCommandExecutor
    -> target Linux server
    -> EvidenceReference(kind=command_result)
```

`EvidenceCollectionService` does not accept raw command text. The command,
timeout and output limit must come from an ALLOW `DiagnosticPolicyResult`.

A denied policy result fails before server lookup or SSH execution.

The default runner reuses the existing project SSH stack. Server-specific
private keys override the default key, and `known_hosts` remains enforced.

Failed commands and expected connection failures are still represented as
Evidence because they can be diagnostically useful:

```text
exit 0      -> success=true
exit != 0   -> success=false
timeout     -> success=false
SSH failure -> success=false
```

Tool output is bounded by `output_limit_chars`. Combined stdout/stderr/error
text is truncated deterministically, while metadata records original character
counts and whether truncation occurred.

Evidence provenance includes server ID, Specialist slug, Tool ID, approved
command, exit status, duration, timeout, output limit, risk and timestamps.
Credentials/private-key paths are not copied into Evidence metadata.

Phase 4.13 returns an in-memory EvidenceReference and introduces no new
database schema.

Runtime acceptance:

```powershell
uv run python tools/collect_diagnostic_evidence.py `
  <SERVER_ID> `
  nginx `
  systemd-status `
  --arguments-json '{"service":"nginx"}'
```

Expected:

```text
Policy: ALLOW
Kind: command_result
SSH executed: YES
```

Phase 4.14 will connect reasoning -> Tool request -> policy -> evidence
collection -> rebuilt context -> next reasoning round under budgets.
