# Current Use Cases

| ID | Name | Actors | Preconditions / permission | Normal result | Alternate/failure result | Related |
|---|---|---|---|---|---|---|
| UC-001 | Register/manage server | Admin | authenticated Admin; `server.write` for writes | persisted server and safety metadata | validation/SSH error; no partial write | FR-001; Admin server tests |
| UC-002 | Configure monitoring profile | Admin | `profile.write` | profile and command assignments persist | invalid command/profile rejected | FR-001; profile tests |
| UC-003 | Run monitoring | Operator/Claude | registered server/profile and bounded command policy | report, executions, Evidence-like structured results persist | timeout/SSH failure becomes controlled failure | FR-002..003 |
| UC-004 | Generate/store report | monitoring service | monitoring cycle | report linked to server/profile | persistence failure is surfaced | FR-003 |
| UC-005 | Analyse report | Claude/Ollama/Python | report available | exact reuse or structured analysis persists | provider failure or malformed output fails closed | FR-004..005 |
| UC-006 | Start investigation | Claude/Operator | analysis claims require investigation | investigation record and candidates persist | healthy/no-candidate path remains no investigation | FR-006 |
| UC-007 | Run Specialists | Specialist loop | selected DB-defined Specialist and bounded policy | read-only tools run; Evidence returned/persisted | policy/budget/tool error stops safely | FR-006..007 |
| UC-008 | Produce final diagnosis | Python/Ollama | owned Evidence and correlated claims | grounded diagnosis with conflict/provenance | missing/foreign Evidence rejected | FR-008, FR-022 |
| UC-009 | Create remediation plan | Claude/Admin | diagnosis and action registry | immutable plan and fingerprint persist | unsupported action or missing Evidence rejected | FR-009 |
| UC-010 | Validate sandbox | Operator/Claude | safe designated target and native attestation | passed validation with Before/After Evidence | unsafe target, stale/mismatch, or unavailable runtime fails closed | FR-010 |
| UC-011 | Request approval | Operator | persisted plan and required sandbox state | approval record bound to plan fingerprint | invalid status/fingerprint rejected | FR-011 |
| UC-012 | Approve/reject remediation | Operator | `remediation.approve` and exact persisted plan | decision is audited; rejection ends path | CSRF/RBAC/expiry/fingerprint failure | FR-011 |
| UC-013 | Execute supervised remediation | Operator | approved exact plan; `remediation.execute` | named action executes, Evidence and execution persist | failure produces controlled status | FR-012 |
| UC-014 | Verify result | Python | execution result | verification and after-state persist | verification failure triggers rollback path | FR-012 |
| UC-015 | Rollback | Operator/Python | registered rollback and `remediation.rollback` | original state restored and audited | rollback failure remains visible and unsafe path stops | FR-012 |
| UC-016 | Discover policy candidate | Viewer/Admin | persisted eligible history | advisory candidate appears | insufficient history/no match yields empty result | FR-013 |
| UC-017 | Create/enable policy | Admin | `autonomous.policy.create/enable` | disabled policy is persisted then explicitly enabled | invalid policy remains disabled | FR-014 |
| UC-018 | Evaluate autonomous remediation | Claude/Python | global gate, policy, plan, Evidence, sandbox, history | evaluator returns one of three outcomes | ambiguity, mismatch, risk, or missing gate denies or requires approval | FR-015..016 |
| UC-019 | Auto-execute safe remediation | Python worker | global opt-in, `AUTO_EXECUTE`, authorization, reservation | one named action executes and is verified | authorization/replay/ownership failure prevents execution | FR-017 |
| UC-020 | Suspend/resume circuit breaker | Python/Operator | failure threshold; Admin resume permission | policy suspends; explicit resume starts new epoch | switch change alone cannot resume | FR-018 |
| UC-021 | Inspect audit trail | Viewer/Operator/Admin | `audit.read` | safe operational and Admin auth events display | secrets/tokens are omitted | FR-019, NFR-AUD |
| UC-022 | Admin login/logout | Admin user | valid credentials | server session cookie, expiry, audit | invalid credentials logged without user enumeration | FR-020 |
| UC-023 | Viewer operations | Viewer | authenticated viewer | read-only screens/APIs | mutating API returns 403 | FR-020; RBAC tests |
| UC-024 | Operator operations | Operator | authenticated operator | monitoring controls and supervised remediation gates | policy management/admin writes return 403 | FR-020 |
| UC-025 | Admin operations | Admin | authenticated Admin + CSRF | manage servers/profiles/Specialists/policies | middleware remains authority | FR-020 |
| UC-026 | Claude bounded tool call | Claude Code | runtime enabled; MCP catalog | typed bounded tool result | unknown/write escalation/raw capability rejected | FR-021 |

## Common failure policy

Authentication, authorization, CSRF, policy, Evidence ownership, plan
fingerprint, sandbox, authorization replay, lease ownership, provider,
database, and SSH failures are represented as controlled failures. The system
does not silently downgrade a blocked action into an unrestricted action.

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
