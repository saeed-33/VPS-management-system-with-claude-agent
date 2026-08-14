# Autonomous Remediation Workflow

```text
diagnosis
  -> trusted issue fingerprint
  -> history/candidate aggregation
  -> policy match (ambiguity denies)
  -> exact plan/Evidence/sandbox/risk gates
  -> AUTO_EXECUTE / REQUIRE_HUMAN_APPROVAL / DENY
  -> single-use authorization
  -> atomic short reservation lease
  -> execute existing named action outside DB transaction
  -> verify / rollback and collect Evidence
  -> conditional owner-token finalize
  -> history, audit, and circuit-breaker update
```

The DB transaction is not held over Ollama or SSH. Concurrent workers cannot
both own a fresh reservation for the same idempotency key, and a stale worker
cannot finalize after ownership changes. Replay of consumed authorization is
blocked.

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
