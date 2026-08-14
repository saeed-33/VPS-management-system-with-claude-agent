# C.14.7 Claude + Ollama runtime requirements

## Ollama context length

The accepted real-runtime smoke demonstrated that Claude Code tool calling requires a sufficiently large Ollama context. Configure at least `OLLAMA_CONTEXT_LENGTH=65536` for local operation.

On Windows:

```powershell
setx OLLAMA_CONTEXT_LENGTH 65536
```

Restart Ollama after changing the value and confirm the active context with `ollama ps`.

## Acceptance gate

A successful monitoring cycle requires `vps` MCP to be connected and must execute at least `mcp__vps__run_monitoring` and `mcp__vps__analyze_report`. A text-only Claude success is not an accepted operational success. Persistence must contain the completed agent job, current report, completed analysis, and any investigation started by the session.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **REFERENCE**

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
