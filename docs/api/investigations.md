# Investigation Read API — Phase 4.19.3

Read-only endpoints:

```text
GET /api/investigations
GET /api/investigations/{investigation_id}
GET /api/reports/{report_id}/investigations
```

The API exposes only persisted Investigation state through
`InvestigationReadService`.

It does not execute Specialists, SSH, tools, correlation, or LLM synthesis.

When no runtime snapshot exists, `runtime_available=false` and `runtime=null`.

Next: Phase 4.19.4 — Investigation Administration UI.
