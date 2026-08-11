# Safety Rule

Claude Code is not the authorization authority.

Claude may request an operation. Python services authorize, execute, persist,
and audit it.

Non-negotiable boundaries:

```text
no unrestricted shell as a normal project tool
no raw production SSH exposed to Claude
no raw production SQL exposed to Claude
no bypass of DiagnosticToolRegistry
no bypass of DiagnosticPolicyEngine
no bypass of Evidence validation
no bypass of SpecialistDefinition permissions
no bypass of budgets
no bypass of Ollama project clients for project LLM reasoning
no production remediation before sandbox validation
ask the user whenever policy requires approval
```

If a requested action would bypass one of these boundaries, stop and use the
project-owned service/tool path or report that the required controlled tool has
not been implemented yet.
