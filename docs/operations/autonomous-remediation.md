# Autonomous Remediation Operations

1. Apply `app/infrastructure/database/migrations/step_7_1_autonomous_remediation.sql`.
2. Run `uv run python tools/bootstrap_database.py --verify-only` and require
   `Tables: 29/29` and `Schema verification: PASS`.
3. Keep `AUTOMATIC_REMEDIATION_ALLOWED=false` until a named low-risk policy,
   explicit service target, rollback path, and verified supervised history are
   reviewed by an operator.
4. Enable a policy through the Admin API. Do not edit the database directly.
5. Monitor `/api/autonomous-remediation/decisions`, `/executions`, and the
   policy runtime endpoint. A failed execution may suspend the policy; resume
   is a manual Admin action.

The autonomous path uses the existing Phase 5/6 SSH, Evidence, verification,
and rollback adapters. Availability of Ollama, SSH, or native sandbox runtime
does not weaken the evaluator: unavailable or stale required evidence is a
denial.
