# C.14.11A.3 — Legacy Runtime and Dependency Removal

## Decision

The operational LLM path is Ollama-only.

Claude Code remains the supervisory orchestration runtime. Python analysis,
specialist reasoning, and final-diagnosis narrative capabilities use Ollama.
The old OpenAI implementations and the unused LangGraph dependency are removed.

## Removed

- `app/domain/analysis/openai_client.py`
- OpenAI final-diagnosis implementation and factory branch
- OpenAI specialist-reasoning implementation and factory branch
- OpenAI settings/provider branch
- direct `openai` dependency
- unused direct `langgraph` dependency
- unused `app/mcp/project_tools.py` compatibility re-export
- duplicate `app/.python-version`

## Preserved

- `LLMAnalysisClient`
- `OllamaAnalysisClient`
- `OllamaFinalDiagnosisNarrativeClient`
- `OllamaSpecialistReasoningClient`
- Analysis and investigation capabilities
- Claude Code runtime
- MCP boundary
- Policy, evidence, persistence, DB, and SSH safety boundaries

## Invariant

Claude decides WHAT/NEXT. Python decides WHETHER ALLOWED and HOW the approved
capability is executed safely.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
