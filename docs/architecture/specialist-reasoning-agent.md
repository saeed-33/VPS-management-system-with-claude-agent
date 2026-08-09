# Specialist Reasoning Agent

**Phase:** 4.10  
**Status:** Implemented — pending runtime acceptance

Phase 4.10 is the first Specialist phase that invokes an LLM.

It is reasoning-only:

```text
SpecialistContextSnapshot
        |
        v
SpecialistReasoningAgent
        |
        v
strict SpecialistReasoningOutput (Pydantic)
        |
reference validation
        |
        v
SpecialistResult
```

No diagnostic tool, SSH command, shell command, service restart, configuration
change, or remediation operation exists in the Phase 4.10 output schema.

## Output contract

The model returns:

```text
summary
confidence
findings[]
hypotheses[]
ruled_out[]
missing_evidence[]
recommended_next_specialists[]
```

Findings contain explicit `evidence_ids` and `knowledge_source_ids`.

## Attribution gate

The LLM is not trusted to invent source IDs.

Before a result can become `SpecialistResult`, every citation is checked
against the actual `SpecialistContextSnapshot`.

Unknown evidence IDs or Knowledge IDs fail validation.

Recommended Specialists may also be checked against the enabled Specialist
Registry. Phase 4.10 only recommends them; it does not spawn them.

## Documentation is not server evidence

The system prompt explicitly separates technical documentation from evidence
about the monitored server. A documentation statement can support how a
component works, but cannot prove that a configuration or fault exists on the
server.

## Missing evidence

`SpecialistResult` now includes `missing_evidence`. This is required for the
next diagnostic phases because a Specialist must be able to say what it needs
to confirm or reject a hypothesis without executing anything yet.

## Provider support

The Phase 4.10 client supports the same configured providers as current report
analysis:

```text
ollama
openai
```

Both paths enforce structured Pydantic output.

## Acceptance

With the current NGINX Knowledge context:

```powershell
uv run python tools/reason_specialist_context.py `
  nginx `
  "Determine what can be concluded about the NGINX failure from the supplied context." `
  --domains nginx,http,proxy
```

A good acceptance result should have:

```text
Status: completed
Confidence: appropriately conservative
Missing evidence: usually > 0 when no live server evidence was supplied
```

The result must not claim that it executed a command or changed the server.

Phase 4.11 introduces the Diagnostic Tool Registry. It still does not grant
arbitrary shell access.
