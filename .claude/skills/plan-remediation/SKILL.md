---
name: plan-remediation
description: Build and supervise a grounded remediation plan from a persisted final diagnosis and Evidence. Use only after an investigation has a persisted final diagnosis; production writes remain approval-gated.
argument-hint: "<investigation_id>"
allowed-tools:
  - mcp__vps__get_investigation
  - mcp__vps__get_investigation_status
  - mcp__vps__get_evidence
  - mcp__vps__propose_remediation
  - mcp__vps__create_remediation_plan
  - mcp__vps__test_remediation_in_sandbox
  - mcp__vps__request_user_approval
  - mcp__vps__apply_approved_remediation
---

# Plan Remediation

## Purpose

Create a grounded, auditable remediation plan and use the supervised Phase 5
lifecycle. No Claude call itself grants approval; execution requires persisted
human approval.

## Input contract

Required:

```text
investigation_id: non-empty persisted investigation ID
```

## Preconditions

1. Call `mcp__vps__get_investigation_status`.
2. Require `final_diagnosis_available == true`.
3. Call `mcp__vps__get_investigation`.
4. Call `mcp__vps__get_evidence`.
5. Require persisted diagnosis claim IDs and Evidence IDs sufficient to ground
   the problem statement.

If grounding is insufficient, return `insufficient_evidence` rather than
inventing a solution.

## Workflow

1. Read the persisted final diagnosis and Evidence.
2. Select only diagnosis claim IDs that exist in the persisted investigation.
3. Select only Evidence IDs returned by project services.
4. Build a concise `problem_summary` from the persisted diagnosis.
5. Call `mcp__vps__propose_remediation` with:
   ```text
   investigation_id
   problem_summary
   diagnosis_claim_ids
   evidence_ids
   ```
6. If the proposal supports a registered action, call
   `mcp__vps__create_remediation_plan`.
7. Call `mcp__vps__test_remediation_in_sandbox` and require a passed result.
8. Call `mcp__vps__request_user_approval` and return the approval ID and plan
   fingerprint to the operator. Stop and wait for the human decision.
9. Only after the operator supplies a persisted human approval ID that is
   approved, call
   `mcp__vps__apply_approved_remediation` with the original server ID. Treat
   the returned execution and verification result as authoritative.

## Hard boundary

This skill must never call raw SSH, arbitrary shell, or an unregistered write
tool. `apply_approved_remediation` is valid only with a human-created,
unexpired approval whose fingerprint still matches the immutable plan.

## Failure behavior

Use controlled domain outcomes where applicable:

```text
no_problem_found
insufficient_evidence
proposal_failed
unsupported_remediation_capability
```

Do not treat "no safe grounded solution" as permission to invent one.

## Stopping conditions

Stop after:

```text
no remediation is needed
grounding is insufficient
the grounded proposal is returned
the proposal tool fails
```

## Output contract

Return:

```text
status
investigation_id
problem_summary
diagnosis_claim_ids
evidence_ids
proposal
approval_required
approval_id
execution_id, when executed
verification_status, when executed
error_code/error_message, when failed
```
