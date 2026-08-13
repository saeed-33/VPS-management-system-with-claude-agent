# C.14.9 Claude-native orchestration

Claude Code is the sole operational workflow orchestrator. Python retains bounded execution capabilities, policy, tool registration, persistence, monitoring execution, analysis capabilities, Specialist execution, and remediation boundaries.

Removed Python orchestration surfaces include the scripted supervised monitoring cycle, scripted multi-Specialist supervisor, ServerCoordinator, and per-server background analysis queues.

MonitoringService now executes and persists monitoring only. Analysis is invoked explicitly through the `analyze_report` MCP tool by Claude. `AnalysisOrchestrator` remains a bounded capability. `SpecialistInvestigationLoop` remains the bounded execution engine for one DB-defined Specialist, while Claude decides which Specialists run and in what order.

When `CLAUDE_RUNTIME_ENABLED=false`, scheduled operational monitoring is disabled. There is no Python orchestration fallback.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **HISTORICAL_CLOSEOUT**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
