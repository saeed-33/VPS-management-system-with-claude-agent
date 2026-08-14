# Capability Architecture

## Monitoring, reports, analysis, and RAG

Monitoring profiles select registered commands and servers. The monitoring
service executes bounded commands through the SSH layer, persists
`monitoring_reports` and `command_executions`, and returns a structured report.
Report services persist and query reports. Analysis first considers exact
reuse, then structured compatibility and hybrid vector/full-text retrieval.
Ollama is called only through the infrastructure adapter and analysis
orchestrator. Knowledge documents/chunks are indexed with PostgreSQL full text
and pgvector; report retrieval documents keep incident retrieval separate from
knowledge retrieval.

## Investigation and Specialists

`InvestigationRouter` converts analysis claims into a bounded candidate list.
The Specialist registry loads DB-defined definitions. `SpecialistInvestigationLoop`
evaluates the diagnostic policy, executes only registered read-only tools,
calls the Specialist reasoning boundary, and invokes
`EvidenceCollectionService.collect(...)`. Correlation preserves conflicts and
the final diagnosis synthesizer produces a grounded diagnosis.

The persisted runtime snapshot stores Specialist execution and Evidence
references. It is not a second Evidence system.

## Remediation

The supervised flow is:

```text
persisted diagnosis -> plan/fingerprint -> native sandbox -> approval
 -> named write execution -> Before/After Evidence -> verification
 -> rollback when required -> audit
```

The autonomous flow adds issue fingerprint, policy/history evaluation,
single-use authorization, short reservation lease, execution outside the DB
transaction, ownership-token finalization, and circuit-breaker accounting.
The existing supervised execution and Evidence services are reused.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

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
