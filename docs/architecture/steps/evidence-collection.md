# Evidence Collection

**Phase:** 4.13  
**Status:** Implemented and runtime accepted

Phase 4.13 is the investigation boundary that performs a real diagnostic action on a target server.

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

`EvidenceCollectionService` does not accept raw command text. Command, timeout, output limit, and risk metadata come from an ALLOW `DiagnosticPolicyResult`.

A denied policy result fails before server lookup or SSH execution.

## Evidence semantics

Failed commands and expected connection failures are still diagnostically useful Evidence:

```text
exit 0      -> success=true
exit != 0   -> success=false
timeout     -> success=false
SSH failure -> success=false
```

Tool output is bounded by `output_limit_chars`. Combined stdout/stderr/error text is truncated deterministically while metadata records original size and truncation state.

## Provenance

Evidence metadata includes:

```text
server ID
Specialist slug
Tool ID
approved command
exit status
duration
timeout
output limit
risk
timestamps
```

Credentials and private-key paths are not copied into Evidence metadata.

## Runtime integration through Phase 4.17

Evidence Collection is consumed by the Specialist Investigation Loop after Policy ALLOW.

Collected Evidence is then:

```text
fed into the next Specialist reasoning round
aggregated by Server Coordinator
propagated across Claude-supervised waves
made available to later dynamic secondary Specialists
```

Evidence remains deduplicated by `evidence_id`.

The 4.17 orchestration path preserves this boundary: secondary Specialists receive accumulated Evidence but cannot bypass Tool Registry, Policy, or Evidence Collection.

## Persistence boundary

Phase 4.13 itself introduced no new schema. Investigation persistence and later orchestration own lifecycle persistence as documented elsewhere.

Phase 4.13 is closed and runtime accepted.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
