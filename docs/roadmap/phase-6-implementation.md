# Phase 6 — Claude-Native Isolated Sandbox Validation

Phase 6 adds a narrow validation gate before human approval:

```text
Claude proposal -> Python plan/policy validation
 -> Claude-native sandbox runtime attestation
 -> explicit safe lab target
 -> Before Evidence -> registered action -> After Evidence
 -> verification -> restoration to original state
 -> fingerprint-bound PASS -> human approval
```

The native sandbox is an agent-isolation boundary, not authorization. Python
continues to own target designation, registered actions, Evidence ownership,
fingerprints, persistence, approval, SSH safety, verification, and cleanup.
The project MCP surface remains 24 tools; the existing
`test_remediation_in_sandbox` tool accepts an explicit Phase 6 target without
adding a shell or sandbox escape capability.

The installed Claude CLI supports the documented `--settings`, `--mcp-config`,
`--strict-mcp-config`, `--add-dir`, and `--permission-mode` flags. It does not
expose a native-sandbox configuration key in its local help output, so the
project does not invent one. Instead, the runtime requires an attestation file
produced from inside the native sandbox proving project access, sensitive-path
denial, and unsandboxed-escape denial. Missing or incomplete attestation fails
closed.

Validation targets must be explicitly designated with `safe-remediation-test`
and `non-production` markers. Validation records bind plan ID, exact plan
fingerprint, target/action, expected/observed state, project-owned Evidence,
verification, cleanup state, timestamps, and audit lifecycle events.

`start_service` and `stop_service` validation restores the prior state. Actions
without a true restoration path, including restart/reload, fail closed.
Approval is prohibited when validation is missing, failed, stale, mismatched,
or incomplete. `automatic_remediation_allowed` remains `false`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **ROADMAP**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
