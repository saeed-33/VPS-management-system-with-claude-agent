# Specialist Reasoning Agent

**Phase:** 4.10+  
**Status:** Implemented and integrated into the bounded Investigation runtime.

The Specialist Reasoning Agent is the LLM reasoning boundary. It does not authorize commands and does not own orchestration.

```text
SpecialistContextSnapshot
        |
        v
SpecialistReasoningAgent
        |
        v
structured output
        |
reference/provenance validation
        |
        v
SpecialistResult
```

## Normal reasoning contract

Normal investigation reasoning may return:

```text
summary
confidence
findings[]
hypotheses[]
ruled_out[]
missing_evidence[]
recommended_next_specialists[]
diagnostic_tool_requests[]
```

Findings may cite Evidence and Knowledge source IDs.

Diagnostic Tool requests contain registered Tool IDs plus typed arguments; they never contain arbitrary shell commands.

## Provenance gate

The LLM is not trusted to invent IDs.

Every referenced Evidence ID must exist in the actual Specialist context. Every Knowledge ID must correspond to an actual retrieved Knowledge source/chunk exposed to the model.

Unknown references fail validation.

Technical documentation is not live server Evidence.

## Secondary Specialist recommendations

`recommended_next_specialists` is advisory output.

The reasoning model does not spawn Specialists. Phase 4.17 Claude-supervised routing validates recommendations against the enabled Specialist Registry, duplicate-execution state, remaining Specialist slots, and remaining action budget.

## Final Synthesis contract

The Investigation Loop can force a synthesis-only pass when no more useful Tool execution should occur.

For the Ollama provider, Final Synthesis intentionally uses a smaller output shape:

```text
summary
confidence
missing_evidence
recommended_next_specialists
```

The purpose is provider reliability: final output must remain complete JSON rather than being truncated while producing verbose findings/hypotheses structures.

Normal reasoning keeps the richer schema.

## Ollama runtime

The accepted Gemma runtime uses an explicit Ollama context window of 32768 tokens.

Context capacity and output generation budget are separate controls. The project keeps a large enough generation allowance for structured output rather than solving truncation by globally reducing output tokens.

## Safety boundary

The reasoning agent cannot execute SSH or raw shell.

```text
LLM Tool request
 -> Diagnostic Tool Registry
 -> Diagnostic Policy
 -> approved execution envelope
 -> Evidence Collection
```

The Policy Engine remains authoritative.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
