# Remediation Rule

Remediation is not authorized as unrestricted autonomous repair.

The fixed workflow allows:

```text
final diagnosis
 -> remediation proposal
 -> isolated-environment validation
 -> policy decision
 -> production application only when allowed
 -> ask the user when approval is required
```

Do not perform production write-capable actions unless project policy authorizes
the action through controlled tools.

Required boundaries:

```text
diagnosis claims must link to evidence
sandbox validation must run before production application
failed sandbox validation blocks production application
high-risk or approval-required actions ask the user
before/after evidence must be persisted when remediation is later implemented
```

Phase C C.1 does not introduce remediation execution tools.
