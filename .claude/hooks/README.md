# Hooks

No hooks are enabled in C.1.

Hooks may be added only when there is a concrete validation or safety need, such
as blocking unsafe project-tool definitions or validating generated Claude
configuration.

Hooks must not become an alternate execution path for monitoring, SSH, SQL, RAG,
LLM analysis, or remediation.
