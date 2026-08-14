# Test Environments

| Environment | Real dependencies | Scope |
|---|---|---|
| Local project | Python, uv, project dependencies | normal unit/interface tests |
| Stable WSL | `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/chat_system` | authoritative current regression run |
| PostgreSQL integration | PostgreSQL + pgvector + configured credentials | schema/bootstrap and real repository checks |
| Ollama | Ollama endpoint/model | real provider/runtime acceptance only |
| Claude/Ollama/MCP | Claude CLI, Ollama, `.mcp.json`, project MCP | opt-in runtime acceptance |
| Native Sandbox | WSL2 and attestation file | Phase 6 sandbox acceptance |
| Remediation lab | explicitly marked non-production server, SSH key, known_hosts | Phase 5/6/7 opt-in acceptance |
| Admin TestClient | SQLite auth fixture and FastAPI TestClient | login/RBAC/CSRF/UI route tests |

Secrets, passwords, private keys, and host-specific paths are intentionally
not documented here.

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
