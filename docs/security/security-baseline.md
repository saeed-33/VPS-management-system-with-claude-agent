# Security Baseline

<!-- DOC-STATUS: CURRENT -->

## Current trust boundary

Phase 4 is approved for supervised diagnostics only.

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Model boundary

The LLM does not receive arbitrary shell access.

It may only request registered Diagnostic Tools using structured parameters.

## Tool boundary

Every executable diagnostic path must pass:

```text
Tool Registry lookup
Specialist allow-list
typed parameter validation
risk/policy checks
round/action/global budgets
```

A DENY decision must never expose or execute a command.

## Evidence / provenance

Claims must reference known Evidence IDs.

Technical Knowledge is not live Evidence.

Unknown Evidence/Knowledge/Claim/Conflict IDs are rejected at the appropriate validation boundary.

## Orchestration

Claude-supervised coordinates workflow but does not override Registry, Policy, Evidence, SSH, or budget rules.

Secondary Specialists must exist in the enabled Registry and fit remaining budgets.

## Provider failure

Invalid/truncated structured output, transport failures, schema-format incompatibility, and timeouts must fail safely or use validated fallback paths.

Provider failure must not bypass Policy.

## Persistence

Runtime snapshots preserve Evidence, claims, conflicts, Final Diagnosis, and narrative references for auditability.

## Readiness gate

Hard safety metrics include:

```text
evidence_grounding
budget_compliance
conflict_preservation
final_diagnosis_grounding
policy_safety
```

These require 100% pass rate in the configured gate.

## Explicitly forbidden in Phase 4

```text
automatic restart
kill process
package install/remove
configuration modification
reboot
firewall changes
arbitrary shell
automatic remediation
```

Phase 5 must define a separate approval/audit/rollback boundary before any of these are considered.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **OPERATIONS**

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
