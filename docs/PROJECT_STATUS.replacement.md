# Project Status

<!-- DOC-STATUS: CURRENT -->

Last synchronized project milestone: **Phase 4.20 complete**.

## Operational status

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

## Accepted readiness evidence

```text
runtime snapshots: 10
persisted runtime observations: 50
controlled safety observations: 30
aggregate observations: 80
readiness metrics passed: 8/8
```

## Accepted metrics

```text
routing_recall              PASS
specialist_completion       PASS
evidence_grounding          PASS
budget_compliance           PASS
conflict_preservation       PASS
final_diagnosis_grounding   PASS
provider_resilience         PASS
policy_safety               PASS
```

## Current product boundary

Implemented:

```text
monitoring
analysis
Incident RAG
Knowledge RAG
dynamic Specialists
deterministic routing
LangGraph orchestration
read-only diagnostic tools
Policy
Evidence
cross-Specialist correlation
Final Diagnosis
runtime persistence
Investigation API/UI
evaluation and safety gate
```

Not implemented/authorized:

```text
automatic remediation
write-capable remediation tools
approval workflow
rollback workflow
```

## Accepted architectural transition

ADR-017 accepts **Claude Code as the primary supervisory orchestration runtime**.

This transition changes orchestration ownership only. Existing Python services
remain authoritative for monitoring, analysis, Incident RAG, Knowledge RAG,
dynamic Specialists, SSH execution, persistence, policy, evidence, and the
Admin/API control plane.

Ollama is the operational LLM provider for project analysis and specialist
reasoning. Claude Code supervises orchestration and must invoke project tools
that use the configured Ollama clients instead of bypassing them.

The transition is additive first: the existing Python/LangGraph path remains
available until Claude-supervised execution passes equivalence and safety gates.

## Fixed operational workflow

```text
periodic monitoring
 -> per-server subordinate agent
 -> monitoring completion
 -> exact/similar historical report lookup
 -> exact match: reuse previous analysis
 -> similar match: pass top 3 similar reports to the LLM
 -> initial LLM analysis and potential issue discovery
 -> if issues exist: select and run specialist agents
 -> specialist deep analysis
 -> subordinate agent aggregates results
 -> final diagnosis
 -> if a problem exists: propose remediation
 -> test remediation in an isolated environment
 -> apply automatically only when policy allows, otherwise ask the user
```

## Next phase

**Phase C - Claude Code Supervisory Runtime Transition.**

Implementation plan:

`docs/roadmap/claude-code-supervisory-transition-plan.md`

Phase 5 - Supervised Remediation follows after Phase C unless a later ADR
changes the ordering.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-11**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
next: Phase C - Claude Code Supervisory Runtime Transition
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
