# Specialist Context Builder

**Phase:** 4.9  
**Status:** Implemented — pending runtime acceptance

Phase 4.9 builds the bounded, specialist-specific context that Phase 4.10 will
send to the Specialist Reasoning Agent.

```text
SpecialistTask
Specialist definition/instructions
Current evidence
Initial analysis
Incident RAG
Knowledge RAG
       |
       v
SpecialistContextBuilder
       |
       +--> SpecialistContextSnapshot
       +--> rendered context
       +--> traceable source references
```

## Important boundary

Phase 4.9 does not call an LLM.

The next phase, 4.10, consumes the context produced here.

## Context budget

Default limits:

```text
evidence items       8
evidence chars       4000
incident contexts    3
incident chars       4500
knowledge chunks     6
knowledge chars      7000
total context chars  18000
```

This prevents a large PDF, website, historical incident set, or command output
from expanding the Specialist prompt without bound.

## Evidence filtering

If a SpecialistTask declares `evidence_ids`, only those evidence records are
included. This prevents unrelated server evidence from leaking into a
specialist-specific context.

## Knowledge query

The query is built from:

```text
Specialist name
task objective
effective domains
Specialist knowledge_topics
initial analysis summary/issues
selected evidence excerpts
```

It is then sent to `KnowledgeHybridRetriever` with the Specialist slug and
domains.

## Attribution

Every retrieved Knowledge Chunk is converted to a
`KnowledgeSourceReference` with stable provenance metadata:

```text
knowledge-chunk:<chunk_id>
chunk_id
document_id
source_id
source_slug
page_number
rank
retrieval strategy
fusion score
```

The rendered context also emits markers such as:

```text
[knowledge:chunk-12]
[incident:report-8/analysis-9]
[evidence:nginx-status]
```

These markers are designed for Phase 4.10 findings/hypotheses to cite their
inputs instead of producing unsupported claims.

## Acceptance

With the currently indexed NGINX source:

```powershell
uv run python tools/inspect_specialist_context.py `
  nginx `
  "Determine which NGINX module/configuration is relevant to this failure." `
  --domains nginx,http,proxy
```

Expected:

```text
Knowledge chunks: > 0
Source refs:      > 0
Context chars:    bounded
```

The rendered context must include Specialist instructions and one or more
`[knowledge:chunk-*]` references.
