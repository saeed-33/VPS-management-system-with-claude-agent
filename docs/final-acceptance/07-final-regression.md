# 07 — Final Regression

## 1. Objective

Run and record the final deterministic regression campaign against the current
worktree without rerunning real Phase 5, Phase 6, Phase 7, or Specialist
acceptance.

## 2. Scope

The campaign covers the complete non-real suite, critical domain regressions,
SPEC-03, SPEC-07, Admin security, deterministic Phase 7 safety, schema and
seed consistency, MCP and Claude/Admin boundaries, safe defaults, compilation,
documentation links, secret sanity, and worktree status.

## 3. Environment

- Date: 2026-08-14.
- Repository: `/mnt/e/AI_VPS_Mamgment/chat_system`.
- Environment: stable WSL project environment with
  `UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system"`.
- Python: 3.14.7; pytest: 8.4.2.
- No real acceptance target or destructive remediation was used.

## 4. Safety constraints

Opt-in real-runtime tests remained skipped. No secrets were printed. Existing
worktree changes were preserved and no unrelated cleanup was performed.

## 5. Exact commands

Full deterministic regression, timed in WSL:

```bash
cd /mnt/e/AI_VPS_Mamgment/chat_system
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/chat_system"
/usr/bin/time -f "ELAPSED_SECONDS=%e" \
  uv run --no-sync python -m pytest -q -r s
```

Focused critical-domain regression:

```bash
uv run --no-sync python -m pytest -q \
  tests/test_error_classification.py \
  tests/test_error_classification_policy.py \
  tests/test_source_location.py \
  tests/test_investigation_runtime_snapshot_service.py \
  tests/test_investigations_api.py \
  tests/test_admin_auth_rbac.py \
  tests/test_admin_remediation_api.py \
  tests/test_admin_system_api.py \
  tests/test_admin_system_web.py \
  tests/test_phase7_acceptance_environment.py \
  tests/test_phase7_acceptance_history.py \
  tests/test_phase7_circuit_breaker.py \
  tests/test_phase7_concurrency_recovery.py \
  tests/test_phase7_negative_security.py \
  tests/test_project_mcp_tool_boundary.py \
  tests/test_claude_least_privilege.py \
  tests/test_seed_specialists.py
```

Deployment-security configuration regression:

```bash
uv run --no-sync python -m pytest -q \
  tests/test_deployment_security_config.py
```

Schema, seed, compilation, documentation, and repository checks:

```bash
POSTGRES_HOST=172.18.128.1 \
  uv run --no-sync python tools/bootstrap_database.py --verify-only
POSTGRES_HOST=172.18.128.1 \
  uv run --no-sync python tools/dev/seed_specialists.py
uv run --no-sync python -m compileall app tests tools
uv run --no-sync python tools/dev/validate_documentation_links.py
git diff --check
```

The lightweight secret sanity check searched tracked files for private-key
headers and common token/session-secret formats without printing values.

## 6. Actual results

```text
FULL_NON_REAL_REGRESSION = PASS
TESTS_COLLECTED = 624
TESTS_PASSED = 620
TESTS_SKIPPED = 4
TESTS_FAILED = 0
TEST_DURATION_SECONDS = 30.00
WARNINGS = 1 existing Starlette/httpx deprecation warning

CRITICAL_DOMAIN_REGRESSION = PASS
SPEC03_REGRESSION = PASS
SPEC07_REGRESSION = PASS
ADMIN_SECURITY_REGRESSION = PASS
PHASE7_DETERMINISTIC_REGRESSION = PASS

DATABASE_SCHEMA = PASS
DATABASE_TABLES = 33/33
PGVECTOR = PASS
RAG_INDEXES = 3/3

SEED_CONSISTENCY = PASS
SPECIALIST_DEFINITIONS = 9

MCP_TOOL_COUNT = 25
MCP_BOUNDARY_REGRESSION = PASS
CLAUDE_ADMIN_SEPARATION = PASS
SAFE_DEFAULTS_REGRESSION = PASS

COMPILEALL = PASS
GIT_DIFF_CHECK = PASS
DOCUMENTATION_LINK_CHECK = PASS
FINAL_SECRET_SANITY = PASS
```

The four skips were the expected opt-in real Claude/Ollama/MCP, Phase 5,
Phase 6, and Phase 7 acceptance tests. The focused critical-domain suite and
the four deployment-security configuration tests also passed. The Specialist
seed reported `Created: 0`, `Updated: 0`, `Skipped: 9`, `Total definitions: 9`.

## 7. Failure and classification

The first WSL schema verification attempt used the `.env` loopback database
host and received connection refused from `127.0.0.1:5432`. This was an
`ENVIRONMENT_DEFECT` in the WSL invocation, not a product or schema defect.
Re-running with the established WSL operational override
`POSTGRES_HOST=172.18.128.1` passed with 33/33 tables, pgvector, and 3/3 RAG
indexes. No production defect was found and no source fix was required.

## 8. Real acceptance policy

No real Phase 5, Phase 6, Phase 7, or Specialist acceptance was rerun. Existing
real acceptance evidence remains authoritative, and no final-regression result
required a change to real execution semantics.

## 9. Worktree status

`git status --short` recorded 65 entries: 48 tracked modifications and 17
untracked entries. The broad categories are 22 app/production entries, 15
test entries, 19 documentation entries, 4 tools entries, and 5 other/config or
generated entries. They include pre-existing production-source, test,
documentation, generated-report, and untracked acceptance artifacts. Those
changes were recorded, not cleaned or discarded. Repository hygiene is
reserved for Step 09.

## 10. Final status

**FINAL_REGRESSION_ACCEPTANCE = PASS**

**PROJECT_CLOSURE_BLOCKING = NO**

## 11. Whether production code changed

No production code changed because of this regression campaign. No regression
defect fix was required.

## 12. Whether commit/push occurred

No commit or push occurred.
