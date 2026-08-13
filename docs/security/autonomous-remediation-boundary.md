# Autonomous Remediation Security Boundary

Phase 7 is fail-closed and Python/database controlled. The global setting
`automatic_remediation_allowed` defaults to `false`. The hard V1 allowlist is
`start_service` with an explicit service target; wildcard targets, raw
commands, arbitrary shell, SQL, raw SSH, and unrestricted tool parameters are
not part of the contract.

The policy evaluator is pure and deterministic. Claude has no policy registry,
authorization, reservation, runtime-state, or kill-switch dependency. Admin
operations are not exposed through MCP. The existing Phase 5 registry remains
the only production write path and supplies the project-owned Before/After
Evidence, verification, and rollback behavior.

Every decision, reservation, authorization, and execution lifecycle boundary
is persisted or written to the existing remediation audit stream. Single-use
authorization is bound to policy version, decision, immutable plan
fingerprint, server, action, target, and sandbox validation. A plan or policy
change invalidates the authorization. Rate limits, cooldown, consecutive
failure suspension, and explicit manual resume provide operational brakes.

This repository's existing Admin surface has no authentication/RBAC provider;
deployment must place the Admin API behind the project's authenticated
operator boundary before enabling autonomy in production.
