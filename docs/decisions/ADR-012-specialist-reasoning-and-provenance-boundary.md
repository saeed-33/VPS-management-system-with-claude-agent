# ADR-012 — Specialist Reasoning Is Structured, Read-Only, and Provenance-Gated

**Status:** Accepted  
**Phase:** 4.9–4.10

## Decision

A Specialist Reasoning Agent receives a bounded
`SpecialistContextSnapshot` and produces structured diagnostic reasoning only.

It does not execute tools in Phase 4.10.

```text
SpecialistTask
+ Specialist instructions
+ current evidence
+ initial analysis
+ Incident RAG
+ Knowledge RAG
        |
        v
SpecialistContextBuilder
        |
        v
SpecialistContextSnapshot
        |
        v
SpecialistReasoningAgent / LLM
        |
        v
strict Pydantic output
        |
        v
reference validation
        |
        v
SpecialistResult
```

## Context budgeting

The current default context budgets are:

```text
evidence items        8
evidence chars        4000
incident contexts     3
incident chars        4500
knowledge chunks      6
knowledge chars       7000
total context chars   18000
```

These limits prevent a large report, PDF, website, or incident history from
expanding the prompt without bound.

## Structured reasoning contract

The LLM returns:

```text
summary
confidence
findings[]
hypotheses[]
ruled_out[]
missing_evidence[]
recommended_next_specialists[]
```

No shell/tool/command field exists in the Phase 4.10 reasoning schema.

## Provenance gate

The model is not trusted to invent identifiers.

Before conversion into `SpecialistResult`:

```text
finding.evidence_ids
    must exist in SpecialistContextSnapshot.evidence

finding.knowledge_source_ids
    must exist in SpecialistContextSnapshot.knowledge_sources

hypothesis supporting/contradicting evidence IDs
    must exist in supplied evidence
```

Unknown evidence or knowledge IDs fail validation.

## Documentation is not proof of server state

Technical documentation can explain how a component behaves.

It cannot by itself prove:

```text
the service is running
the configuration exists
the upstream is down
a port is listening
a fault occurred
```

Those claims require operational Evidence.

The Specialist system prompt explicitly enforces this distinction.

## Recommended Specialists

LLMs may use conceptual names which differ from persisted Specialist slugs.

The accepted normalization policy is:

```text
systemd    -> systemd-service
network    -> linux-network
cpu        -> linux-cpu
memory     -> linux-memory
storage    -> linux-storage
process    -> linux-process
postgres   -> postgresql
```

Only aliases with deterministic mappings are accepted.

Unknown recommendations are dropped rather than fabricated and are recorded
in:

```text
metadata["dropped_specialist_recommendations"]
```

The reasoning result must not fail merely because an otherwise valid response
suggested an unregistered conceptual Specialist.

## Runtime acceptance

The NGINX reasoning acceptance had no operational server evidence.

The model correctly returned:

```text
status          completed
confidence      0.10
findings        0
hypotheses      1
missing evidence 5
```

It explicitly requested NGINX service status, logs, listener evidence, and
upstream health rather than claiming those facts were known.

This conservative result is the intended behavior.

## Consequences

- Unsupported claims are easier to detect.
- Missing evidence is a first-class diagnostic output.
- Knowledge citations remain traceable.
- Tool use can be introduced later without mixing reasoning and execution.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.

> Historical document — not current architecture.
<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_ADR**

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
