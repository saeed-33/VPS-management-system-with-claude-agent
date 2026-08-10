# Diagnostic Policy Engine

**Phase:** 4.12  
**Status:** Implemented — pending acceptance

The Diagnostic Tool Registry defines which capabilities exist. The Diagnostic
Policy Engine decides whether one Tool Request may proceed.

```text
Specialist Tool Request
        |
        v
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

Phase 4.12 does not execute SSH.

## Inputs

```text
SpecialistRuntimeDefinition
DiagnosticToolCall
round_number
specialist_actions_used
investigation_actions_used
InvestigationBudget
```

The Specialist supplies `allowed_tool_ids`, `max_rounds`, and `max_actions`.

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
risk / requires_sudo metadata
```

A DENY result never exposes command text.

Phase 4.13 must consume this approved envelope rather than reconstructing
commands from LLM output.

## Budget semantics

`actions_used` means actions already consumed.

```text
used < max_actions   -> a new action may proceed
used >= max_actions  -> deny
```

The current round must fit both Specialist and Investigation round limits.

## Risk boundary

The default policy admits only:

```text
read_only
```

No remediation/write risk class is admitted in Phase 4.

## Security properties

```text
no SSH execution
no investigation mutation
no arbitrary shell input
no unassigned Tool capability
no argument rendering for unauthorized Tools
```

## Acceptance

After assigning `systemd-status` to the nginx Specialist:

```powershell
uv run python tools/inspect_diagnostic_policy.py `
  nginx `
  systemd-status `
  --arguments-json '{"service":"nginx"}'
```

Expected:

```text
Decision: ALLOW
SSH executed: NO
```

For an unassigned Tool, expect `DENY` with `tool_not_allowed`.

## Next

Phase 4.13 — Evidence Collection will execute only approved envelopes using the
existing bounded SSH implementation and convert results into attributed
Evidence.
