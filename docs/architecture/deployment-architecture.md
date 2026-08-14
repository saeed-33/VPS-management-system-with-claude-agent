# Deployment and Physical Architecture

The supported deployment has a Python application process, PostgreSQL with
pgvector, Ollama, the Claude Code CLI when the supervisory runtime is enabled,
the project MCP server process, and one or more managed Linux VPS targets.

```text
Developer/Admin browser
        |
        v
FastAPI/Uvicorn host ---- PostgreSQL + pgvector
        |                 \
        |                  Ollama host/model
        |
        +-- Claude Code CLI -- project vps MCP server
        |
        +-- known-hosts SSH --> designated VPS targets
```

The application host stores no plaintext session token or password verifier
input. SSH private keys and `known_hosts` are configured paths outside the
documentation and must be protected by deployment permissions. Real
acceptance requires a separately designated non-production lab, native
Sandbox/WSL2 evidence for Phase 6, and explicit opt-in variables. The default
configuration is safe for non-autonomous operation: LLM/runtime and automatic
remediation switches are not implicitly enabled.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-14**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / evidence reconciliation required
Phase 6 readiness: conflicting repository records
Phase 7: implemented / live acceptance record not present
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
