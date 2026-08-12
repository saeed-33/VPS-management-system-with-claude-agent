# Claude Runtime Safety Invariants

These rules apply to every project Claude workflow.

Claude is a requester and coordinator. Python project services remain the
authorization and execution authority.

Never use or introduce a normal-operation path that bypasses:

```text
project MCP tools
DiagnosticToolRegistry
DiagnosticPolicyEngine
Evidence validation
SpecialistDefinition permissions
investigation budgets
PostgreSQL persistence
configured Ollama project/runtime path
remediation policy and approval gates
```

Forbidden normal-operation capabilities:

```text
unrestricted shell
raw production SSH
raw production SQL
direct database modification
direct production write remediation
hard-coded domain Specialists as the source of truth
```

A tool result that is denied, unsupported, unavailable, or incomplete is a
valid controlled outcome. Do not bypass the boundary to obtain the result by
another mechanism.

Production remediation remains unauthorized until Phase 5 explicitly introduces
and accepts the required write-tool, policy, approval, verification, rollback,
and audit contracts.
