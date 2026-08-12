# Evidence and Provenance Invariants

Claims about current server state must be grounded in current report data or
persisted Evidence returned by project services.

Historical Incident RAG and Knowledge RAG are context sources. They may support
interpretation and hypotheses, but they are not proof that the same condition is
currently present.

Never fabricate or silently rewrite project identifiers, including:

```text
report IDs
analysis IDs
investigation IDs
Specialist IDs/slugs
Evidence IDs
Knowledge source/chunk IDs
claim IDs
conflict IDs
remediation plan/result IDs
```

When evidence is missing, conflicting, stale, or insufficient, preserve that
uncertainty explicitly.

Dynamic Specialist definitions come from the database-backed project registry.
Only enabled Specialists and their persisted instructions, allowed tool IDs,
and budgets are authoritative.

Final diagnosis and later remediation proposals must preserve traceability back
to the evidence and project records that support them.
