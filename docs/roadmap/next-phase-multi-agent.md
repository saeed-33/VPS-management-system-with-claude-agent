# Future Phase 5 - Supervised Remediation

<!-- DOC-STATUS: REFERENCE -->

Phase 4 autonomous diagnosis is complete and has passed the Production
Readiness Gate.

ADR-017 inserts **Phase C - Claude Code Supervisory Runtime Transition** before
Phase 5. This document remains the future Phase 5 remediation reference, not
the immediate next implementation phase.

Current state:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Phase 5 objective

Introduce **supervised remediation**, not unrestricted autonomous repair.

The first deliverable should define contracts and approval semantics before
adding any write-capable action.

Recommended sequence:

```text
5.1 Remediation contracts + approval model
5.2 remediation risk classification
5.3 dry-run / proposed command representation
5.4 approval persistence + audit
5.5 bounded write-capable tool registry
5.6 before/after Evidence
5.7 verification and rollback
5.8 supervised remediation UI/API
5.9 safety evaluation
5.10 remediation readiness gate
```

## Required boundary

Until Phase 5 explicitly grants a capability:

```text
NO automatic restart
NO kill
NO package install/remove
NO config write
NO reboot
NO firewall modification
NO arbitrary shell
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
next: Phase C - Claude Code Supervisory Runtime Transition
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
