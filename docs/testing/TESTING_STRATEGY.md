# Testing Strategy

<!-- DOC-STATUS: CURRENT -->

Testing must establish implementation, safety, persistence, and runtime truth.
`pytest` is necessary but is not sufficient for Claude/Ollama/MCP or
Evidence/policy changes.

## Accepted current baseline

```text
normal full suite:              417 passed, 1 skipped, 1 warning
architecture suite:              6 passed
C.14.12 focused suite:          26 passed
real runtime acceptance:          PASS
readiness dimensions:          8 / 8 PASS
```

The one warning is the existing Starlette/httpx deprecation warning. Real
runtime tests are opt-in and require external infrastructure.

## Test layers

### Unit and contract tests

```powershell
uv run python -m pytest
```

These cover contracts, configuration, routing, Specialists, retrieval,
Ollama clients, policy, Evidence, SSH boundaries, persistence, MCP schemas,
Admin/API wiring, runtime jobs, and observability.

### Architecture tests

```powershell
uv run python -m pytest tests/test_architecture_dependencies.py -v
```

These verify dependency direction and absence of the removed application
packages.

### Controlled safety evaluation

```powershell
uv run python tools/acceptance/run_safety_runtime_evaluation.py
```

This runs real routing, policy, registry, parser, retry, timeout, and fail-closed
logic with deterministic controlled failure transport. It covers routing recall,
provider resilience, and policy safety.

### Persisted runtime evaluation

```powershell
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 100
```

This measures persisted Specialist completion, Evidence grounding, budgets,
conflict preservation, and final diagnosis grounding from real snapshots.

### Aggregate readiness evaluation

```powershell
uv run python tools/acceptance/run_production_readiness_evaluation.py \
  --server-id <server_id> --limit 100 \
  --output artifacts/evaluation/c14_12_readiness.json
```

The accepted C.14.12 result is 8/8 PASS. Do not regenerate the accepted gate
from fake data.

### Real runtime acceptance

```powershell
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="ollama"
$env:CLAUDE_RUNTIME_ENABLED="true"
$env:AI_VPS_REAL_RUNTIME_SERVER_ID="<server_id>"
$env:AI_VPS_RUN_REAL_RUNTIME_TESTS="1"
uv run python -m pytest tests/real_runtime/test_c14_11_claude_ollama_mcp_acceptance.py -v -s
```

This requires native Claude CLI, Ollama and the configured model, PostgreSQL,
the project MCP server, SSH private key/known_hosts, and a reachable managed
VPS. It verifies AgentJob/session, MCP, report, analysis, and controlled
failure/success persistence. It is not run by the normal suite.

## Required validation order

For runtime, policy, Evidence, budget, or architecture changes:

1. focused tests;
2. architecture tests when boundaries change;
3. full `pytest`;
4. controlled safety evaluation;
5. persisted readiness evaluation;
6. real runtime acceptance when infrastructure is available.

No test may bypass the Policy Engine, Evidence validation, budgets, known-hosts
SSH boundary, or automatic-remediation flag.

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
