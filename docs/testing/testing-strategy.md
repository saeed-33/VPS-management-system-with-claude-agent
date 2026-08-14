# Testing Strategy

## Layers

1. Static checks: compileall, route inventory, project MCP catalog, and
   `git diff --check`.
2. Unit tests: pure contracts, policies, fingerprints, routing, parsers,
   retrieval, Specialist loop, and evaluator behavior.
3. Repository integration: SQLite fixtures for repositories and service
   persistence; PostgreSQL bootstrap verification for the real schema.
4. Interface tests: FastAPI TestClient for APIs, Jinja pages, Admin roles,
   CSRF, error responses, and UI source contracts.
5. Security/negative tests: unknown tools, bad Evidence, bypass attempts,
   replay, mismatches, unavailable providers, unsafe target, and raw capability
   exposure.
6. Concurrency/recovery: leased reservations, owner-token finalization,
   competing workers, interrupted jobs, and circuit-breaker recovery.
7. Real acceptance: explicit opt-in Claude/Ollama/MCP, Phase 5 lab, Phase 6
   native Sandbox, and Phase 7 autonomous lab tests. These are not part of the
   normal suite and are not rerun for documentation.

## Test interpretation

Green deterministic tests prove local contracts and failure semantics. They do
not prove live SSH, native Sandbox, Ollama, Claude CLI, or social delivery.
Real acceptance evidence must include environment preflight, safe target
designation, cleanup/restoration, and auditable outputs.

## Performance

The code defines command/SSH/LLM timeouts and concurrency limits, but the
repository has no current production load benchmark. Performance requirements
therefore distinguish configured limits from unmeasured p95 latency.

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
