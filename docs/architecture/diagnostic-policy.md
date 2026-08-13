# Diagnostic Policy Engine

**Phase:** 4.12  
**Status:** Implemented and runtime accepted

The Diagnostic Tool Registry defines which capabilities exist. The Diagnostic Policy Engine decides whether one Tool Request may proceed.

```text
Specialist Tool Request
        |
Diagnostic Policy Engine
        |
        +-- registered?
        +-- assigned to Specialist?
        +-- allowed risk?
        +-- Specialist round budget?
        +-- Investigation round budget?
        +-- Specialist action budget?
        +-- Investigation action budget?
        +-- typed arguments valid?
        |
        +--> DENY
        |
        `--> ALLOW + approved execution envelope
```

The Policy Engine itself does not execute SSH.

## Inputs

```text
SpecialistRuntimeDefinition
DiagnosticToolCall
round_number
specialist_actions_used
investigation_actions_used
InvestigationBudget
```

## Explicit denial reasons

```text
unknown_tool
tool_not_allowed
unsupported_risk
invalid_arguments
specialist_round_limit
investigation_round_limit
specialist_action_limit
investigation_action_limit
```

## Approved execution envelope

Only an ALLOW result exposes:

```text
rendered_command
timeout_seconds
output_limit_chars
risk
requires_sudo metadata
```

A DENY result never exposes command text.

Phase 4.13 Evidence Collection consumes this approved envelope rather than reconstructing commands from LLM output.

## Budget semantics

`actions_used` means actions already consumed.

```text
used < max_actions   -> a new action may proceed
used >= max_actions  -> deny
```

Only actual approved SSH executions later consume action budget.

## Risk boundary

The current Phase 4 policy admits only:

```text
read_only
```

No remediation/write risk class is admitted.

## Runtime role

The Policy Engine remains mandatory inside every Specialist Investigation Loop,
including:

```text
single-Specialist execution
Claude-supervised server sessions
Claude-supervised parallel workers
DB-defined Specialist runs and follow-up waves
```

Neither Claude-supervised nor the Coordinator may bypass Policy.

## Security properties

```text
no arbitrary shell input
no unassigned Tool capability
no argument rendering for unauthorized Tools
no SSH execution on DENY
bounded round/action execution
```

This boundary is accepted by C.14.12 and remains required for all supervised
diagnostic operations.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
