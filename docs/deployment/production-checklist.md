# Production / Supervised Operations Checklist

<!-- DOC-STATUS: CURRENT -->

This checklist applies to the current supervised and explicitly policy-gated
remediation system. Automatic remediation remains disabled by default.

## Required state

```text
Production Readiness Gate = PASS
readiness = ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Deployment security configuration

- `DEBUG=false` in production; local `DEBUG=true` is explicit development only.
- `ADMIN_SESSION_SECRET` is supplied externally, stable across restarts, and
  at least 32 characters; it is never committed, logged, or shown in the UI.
- `ADMIN_SESSION_SECURE=true` is set when served through HTTPS.
- Internet traffic terminates at an HTTPS reverse proxy, which forwards only
  to the internal FastAPI listener (`127.0.0.1:8000` or an approved private
  interface). Do not expose direct Uvicorn without firewall/proxy controls.
- PostgreSQL is private/internal only; database credentials are external
  configuration and the application user has only required database access.
- Ollama listens on localhost/private network only and is not Internet-facing.
- MCP is internal/project-scoped and remains a bounded 25-tool surface.
- SSH private keys and `known_hosts` are provisioned outside the repository;
  host-key verification remains enabled.
- Automatic remediation is false until an operator explicitly enables a
  reviewed policy; backups, log permissions, and credential rotation are
  verified operationally.

## Application

- Environment variables validated.
- Database reachable.
- Required migrations applied.
- FastAPI health endpoint succeeds.
- Route inventory matches expected API/web surface.
- Scheduler configuration reviewed.
- Secrets are not committed.

## Ollama / LLM

- Configured provider reachable when LLM is enabled.
- Model name verified.
- Runtime context explicitly configured.
- Structured-output compatibility/retry path tested.
- Provider failure is fail-safe.

Reference accepted local model family during Phase 4 testing:

```text
gemma4:e4b-it-q4_K_M
context 32768
```

This is a reference, not a hard requirement for every deployment.

## Linux / SSH

- Test connection succeeds for monitored servers.
- Monitoring user privileges are least-privilege.
- No arbitrary shell capability is exposed to the model.
- Diagnostic Tool Registry contains only reviewed tools.
- Policy DENY cannot reach SSH execution.

## Evaluation

Run:

```powershell
uv run python -m pytest
uv run python tools/acceptance/run_evaluation_dataset.py
uv run python tools/acceptance/run_safety_runtime_evaluation.py
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 500
uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500
```

The final command must report:

```text
Production Readiness Gate: PASS
```

## Operational restrictions

Do not enable or manually wire in unregistered write-capable actions such as
restart, kill, package changes, configuration writes, firewall changes, or
reboot. Phase 5/6/7 write paths remain bounded by registration, approval,
sandbox, rollback, Evidence, and policy gates.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **OPERATIONS**

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
