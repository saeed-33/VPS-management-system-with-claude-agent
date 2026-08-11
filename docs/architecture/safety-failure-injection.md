# Safety & Failure Injection — Phase 4.20.4

Phase 4.20.4 measures the three readiness metrics that cannot be established from persisted Investigation snapshots alone:

```text
routing_recall
provider_resilience
policy_safety
```

Ten controlled cases execute the real deterministic InvestigationRouter.

Ten controlled cases execute the real DiagnosticPolicyEngine and cover safe allow/deny boundaries, typed argument rejection, and round/action budgets.

Ten controlled cases execute the real OllamaSpecialistReasoningClient through httpx.MockTransport. The HTTP/provider behavior is controlled, while schema fallback, retry, JSON validation, compatibility handling, and safe failure behavior are the production client logic.

No SSH commands or database writes are performed.

Automatic remediation remains disabled.

Phase 4.20.5 combines these observations with persisted-runtime observations from Phase 4.20.3 and evaluates the aggregate Production Readiness Gate.
