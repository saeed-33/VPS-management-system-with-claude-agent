
## ADR-017 - Claude Code as Supervisory Agent Runtime

**Accepted.** Claude Code becomes the primary supervisory orchestration runtime
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

Migration is additive first, with the current orchestration path retained until
equivalence and safety gates pass. See
`ADR-017-claude-code-supervisory-agent-runtime.md`.
