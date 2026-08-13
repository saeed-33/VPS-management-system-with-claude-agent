
## ADR-017 - Claude Code as Supervisory Agent Runtime

**Accepted.** Claude Code is the supervisory orchestration runtime
for the fixed operational workflow: periodic monitoring, per-server subordinate
agent, exact/similar historical report lookup, Ollama-backed analysis,
dynamic Specialist execution, final diagnosis, remediation proposal,
isolated-environment validation, and policy/user-gated production application.

Existing Python services remain authoritative for monitoring, analysis,
Incident RAG, Knowledge RAG, Specialists, SSH, persistence, policy, evidence,
budgets, sandbox validation, and the Admin/API control plane. Ollama is the
operational LLM provider for project analysis and specialist reasoning. The
integration boundary is controlled project tools/MCP; no unrestricted shell,
raw SSH, raw SQL, Ollama-client bypass, or policy bypass is authorized.

Claude Code performs supervisory orchestration through project tools. See
`ADR-017-claude-code-supervisory-agent-runtime.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

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
