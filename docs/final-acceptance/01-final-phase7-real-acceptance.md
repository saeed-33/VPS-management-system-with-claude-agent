# 01 — Final Phase 7 Real Acceptance

## 1. Objective

Prove the Phase 7 autonomous-remediation flow against the designated
non-production target, including authorization, policy evaluation, execution,
verification, restoration, audit history, and replay protection.

## 2. Scope

The real Phase 7 acceptance test covered the project-owned service-state
Evidence path and the autonomous plan, decision, authorization, reservation,
execution, verification, cleanup, and idempotency boundaries.

## 3. Preconditions

- The explicitly designated non-production `phase5-lab` target was available.
- PostgreSQL, the project runtime, SSH access, known-hosts validation, and the
  required native runtime were configured.
- The target service was expected to be restored to its original state.
- Automatic remediation remained disabled by default outside the test scope.

## 4. Environment

- Date: 2026-08-14.
- Stable WSL project environment with the repository at
  `E:\AI_VPS_Mamgment\chat_system`.
- The test used the project test environment and a non-production target.
- Environment variable names used by the test include `POSTGRES_HOST`,
  `DEFAULT_SSH_PRIVATE_KEY_PATH`, and `SSH_KNOWN_HOSTS_PATH`. Secret values and
  private-key contents are intentionally not recorded.

## 5. Safety constraints

- No production target was used.
- Only the named project-owned service-state action was eligible.
- Authorization was single-use and fingerprint-bound.
- Verification and final-state restoration were required.
- A duplicate execution had to be blocked.
- The acceptance did not enable automatic remediation globally.

## 6. Exact commands or procedure

The acceptance procedure was the opt-in real-runtime test:

```bash
export AI_VPS_RUN_REAL_RUNTIME_TESTS=1
uv run --no-sync python -m pytest tests/real_runtime/test_phase7_real_autonomous_acceptance.py -q -r s
```

The operator first ran the preflight and the acceptance attempt, inspected the
SSH path, restored the WSL bridge, and reran the same acceptance procedure.

## 7. Expected acceptance gates

Preflight, project Evidence collection, candidate eligibility, `AUTO_EXECUTE`,
authorization consumption, successful execution, verification, final state
restoration, policy cleanup, audit history, and replay blocking must all pass.

## 8. Actual results

### Attempt 1 — failed before autonomous execution

- Preflight: **PASS**.
- Windows upstream `172.18.128.1:2223`: **PASS**.
- WSL `127.0.0.1:2222`: **no listener**.
- Direct connection: **refused**.
- Project-owned service-state Evidence: **FAIL**.
- No autonomous execution was reached.

Root cause: the WSL `socat` SSH bridge was not running. This was an
environment/transport failure, not a Phase 7 application failure.

### Correction and rerun

The bridge was restored so that `127.0.0.1:2222` forwarded to
`172.18.128.1:2223`. The project-owned Evidence check then passed with
`observed_state=inactive`.

### Attempt 2 — passed

- Pytest exit code: `0`.
- Final result: `FINAL_REAL_PHASE7_ACCEPTANCE = PASS`.
- `execution_status=succeeded`.
- `final_policy_status=disabled`.
- `final_state_restored=true`.
- `verification_status=verified`.
- `supervised_execution_count=18`, `verified_success_count=18`,
  `failed_execution_count=0`.
- Duplicate/replay execution was blocked.

## 9. Evidence / IDs

- `authorization_id`: `7595b273-f170-4a38-8e1c-c13f4507fe5b`
- `authorization_status`: `consumed`
- `autonomous_plan_id`: `phase7-real-autonomous-f8a52ea008e746e0b156048c9824d936`
- `candidate_eligible`: `true`
- `decision_id`: `fb7752f8-e74a-4238-a0d8-65e228a07f38`
- `decision_outcome`: `auto_execute`
- `execution_id`: `f566819f-b911-4194-8cff-3a759d7f2045`
- `issue_fingerprint`: `bd749a1930d447aac52c12fa17a5eded495f7e3bc03fcc71b38441c730ad77c5`
- `policy_id`: `phase7-real-policy-0cd0082462b4470b827df29c352dc1a3`
- `policy_version`: `1`
- `reservation_id`: `21c0f689-749c-44cc-9814-2422dc325868`
- `sandbox_validation_id`: `1467c9be-0b3e-44fb-988a-8ae61de94024`

## 10. Failed attempts

The initial attempt failed at project Evidence collection because the WSL SSH
transport bridge was absent. It is retained here and was not deleted or
reclassified as an application failure.

## 11. Root cause if failure occurred

The failed attempt was caused by a missing WSL `socat` SSH bridge. The upstream
Windows endpoint was reachable, but the expected WSL forwarding listener was
not present.

## 12. Fix performed

The WSL bridge was restored from `127.0.0.1:2222` to `172.18.128.1:2223`.
No application architecture or production code change was required for this
transport correction.

## 13. Revalidation

The project Evidence check passed after restoration, and the complete real
Phase 7 acceptance rerun passed with exit code `0`. The final state was
verified as restored and the policy was disabled.

## 14. Remaining blockers

No Phase 7 blocker remains in this record. This result does not close the
separate Specialist, Admin UI, specification, deployment, regression, report,
or repository-hygiene acceptance steps.

## 15. Final status

**FINAL_REAL_PHASE7_ACCEPTANCE = PASS**

The initial failure did **not** prove a Phase 7 application defect; it proved
that the required WSL SSH transport bridge was missing at that time.

## 16. Whether production code changed

No production application code changed as part of the documented Phase 7
acceptance correction. The correction was an environment/transport change.

## 17. Whether commit/push occurred

No commit or push occurred.

## 18. Current-worktree status after SPEC-03

On 2026-08-14, the current worktree was reviewed after SPEC-03 introduced
explicit autonomous denial for `dangerous` and `sensitive` findings.

`CURRENT_WORKTREE_REAL_PHASE7_ACCEPTANCE = PASS`

The safe real autonomous-remediation path remained operational under that
gate. This deployment-security audit did not rerun Phase 7 and did not reopen
its closed real-acceptance record.
