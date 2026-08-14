# Autonomous Remediation Operations

1. Apply `app/infrastructure/database/migrations/step_7_1_autonomous_remediation.sql`.
2. Run `uv run python tools/bootstrap_database.py --verify-only` and require
   `Tables: 33/33` and `Schema verification: PASS` after the additive Admin
   authentication migration has been applied.
3. Keep `AUTOMATIC_REMEDIATION_ALLOWED=false` until a named low-risk policy,
   explicit service target, rollback path, and verified supervised history are
   reviewed by an operator.
4. Enable a policy through the Admin API. Do not edit the database directly.
5. Monitor `/api/autonomous-remediation/decisions`, `/executions`, and the
   policy runtime endpoint. A failed execution may suspend the policy; resume
   is a manual Admin action. Resume clears the consecutive-failure counter,
   clears the suspension marker, and starts a new runtime epoch; it never
   happens automatically after a process restart or global-switch change.
   Evaluator denials (for example missing sandbox, policy mismatch, or the
   global kill switch) are pre-write safety decisions and do not increment
   the execution-failure counter. Registered execution failures,
   verification failures, and rollback failures do.

The autonomous path uses the existing Phase 5/6 SSH, Evidence, verification,
and rollback adapters. Availability of Ollama, SSH, or native sandbox runtime
does not weaken the evaluator: unavailable or stale required evidence is a
denial.
