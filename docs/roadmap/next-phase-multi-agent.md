# Phase 5 - Supervised Remediation

<!-- DOC-STATUS: REFERENCE -->

Phase 4 autonomous diagnosis is complete and has passed the Production
Readiness Gate.

ADR-017 defines Claude Code as the supervisory runtime. Phase 5 must expose
remediation capabilities as controlled project tools and let Claude coordinate
the fixed remediation workflow through those tools.

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

Claude-native rule for every Phase 5 step:

```text
If Claude can plan, sequence, classify, compare evidence, or synthesize the
operator-facing recommendation, do not rebuild that coordination in Python.
Python provides the tool contract, deterministic validation, policy enforcement,
persistence, sandbox execution, and audit trail.
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
Document classification: **ROADMAP**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
