# Testing and Evaluation

Run:

```powershell
uv run python -m pytest
```

## Current automated baseline

After Phase 4.4 acceptance:

```text
57 passed
```

Current suite covers RAG invariants plus Phase 4 Foundation contracts, dynamic Specialist persistence, Specialist Management API, effective FastAPI route inventory, and Specialist Registry behavior.

Registry tests cover:

- disabled Specialists excluded.
- stable snapshots.
- deterministic ordering.
- case-insensitive domain lookup.
- multi-domain matching.
- `require_all` filtering.
- malformed enabled definitions rejected.
- duplicate domains normalized.

Manual 4.4 acceptance:

```text
Enabled definitions: 9

--domain cpu
-> linux-cpu

--domains cpu,process
-> linux-cpu        100%
-> linux-memory      50%
-> systemd-service   50%
-> linux-process     50%
```

This validates Registry candidate discovery. Phase 4.5 owns final selection.

The existing RAG E2E baseline remains documented by `tools/evaluate_rag.py`.
