---
name: plan-remediation
description: Produce a grounded remediation proposal from a persisted final diagnosis and Evidence without authorizing or executing production changes. Use only after an investigation has a persisted final diagnosis.
argument-hint: "<investigation_id>"
allowed-tools:
  - mcp__vps__get_investigation
  - mcp__vps__get_investigation_status
  - mcp__vps__get_evidence
  - mcp__vps__propose_remediation
---

# Plan Remediation

## Purpose

Create a grounded remediation proposal only.

The current Phase C gate does not authorize production remediation, request
production approval, or execute write-capable actions. Phase 5 introduces the
accepted write-tool, approval, verification, rollback, and audit contracts.

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
6. Return the project proposal and explicitly report:
   ```text
   production_application_allowed = false
   ```

## Hard boundary

This skill must not call:

```text
mcp__vps__create_remediation_plan
mcp__vps__test_remediation_in_sandbox
mcp__vps__request_user_approval
mcp__vps__apply_approved_remediation
```

Those capabilities remain outside this pre-Phase-5 operational skill.

The existing Phase C remediation service is scaffolding; it is not evidence of
a real isolated sandbox or production write executor.

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
production_application_allowed: false
error_code/error_message, when failed
```
