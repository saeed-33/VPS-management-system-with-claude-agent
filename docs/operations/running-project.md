# Running the Project

<!-- DOC-STATUS: CURRENT -->

## Development environment

From the project root:

```powershell
uv sync
```

Configure `.env` from `.env.example`.

## Start the application

```powershell
uv run python -m uvicorn app.main:app --reload
```

Default local development endpoint is typically:

```text
http://127.0.0.1:8000
```

Use the configured environment as the source of truth.

## Health and routes

```powershell
uv run python tools/list_routes.py
```

## Test the project

Quick regression:

```powershell
uv run python -m pytest
```

Documented full deterministic sequence:

```powershell
uv run python tools/run_all_tests.py --mode full
```

Readiness sequence:

```powershell
uv run python tools/run_all_tests.py --mode readiness --limit 500
```

See:

```text
docs/testing/TESTING_STRATEGY.md
docs/testing/TEST_CATALOG.md
docs/testing/RUNTIME_SCENARIOS.md
```

## Production-readiness report

```powershell
uv run python tools/run_production_readiness_evaluation.py --limit 500
```

Current accepted Phase 4 state is:

```text
ready_for_supervised_operations
automatic_remediation_allowed = false
```

## Random Linux test workloads

On a disposable Linux test VM:

```bash
python3 tools/linux_scenarios/random_linux_workload.py \
  --scenario random \
  --seed 20260811 \
  --duration 20
```

Or:

```bash
python3 tools/linux_scenarios/run_linux_scenario_matrix.py \
  --seed 20260811 \
  --duration 10
```

These scripts are bounded workload generators, not remediation tools.

## Documentation maintenance

After adding/removing tests or files:

```powershell
uv run python tools/generate_test_catalog.py
uv run python tools/generate_project_structure.py
uv run python tools/sync_documentation.py
uv run python tools/audit_documentation.py
```

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
