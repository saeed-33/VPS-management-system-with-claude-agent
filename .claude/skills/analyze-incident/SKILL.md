---
name: analyze-incident
description: Analyze one persisted monitoring report using exact historical lookup, top-3 Incident RAG context when needed, and the project AnalysisOrchestrator. Use after monitor-server returns a persisted report.
argument-hint: "<report_id>"
allowed-tools:
  - mcp__vps__get_report
  - mcp__vps__find_exact_report_match
  - mcp__vps__get_top_similar_reports
  - mcp__vps__analyze_report
  - mcp__vps__get_analysis
---

# Analyze Incident

## Purpose

Produce or reuse the persisted analysis for one report without bypassing the
project AnalysisOrchestrator or its configured Ollama/RAG behavior.

Historical reports are context. They are not proof of current server state.

## Input contract

Required input:

```text
report_id: positive integer
```

## Preconditions

1. Call `mcp__vps__get_report`.
2. Stop if the report cannot be read.
3. Do not accept a historical analysis as the current report's persisted
   analysis unless the project orchestrator persists/reuses it for the current
   report.

## Workflow

1. Read the current report.
2. Call `mcp__vps__find_exact_report_match`.
3. Record whether an exact completed historical analysis was found.
4. If exact lookup succeeds with `matched == false`, call
   `mcp__vps__get_top_similar_reports` with `limit: 3`.
5. If exact lookup itself fails, record a retrieval warning and still attempt
   top-similar retrieval before analysis.
6. Treat top-similar retrieval failure as degraded historical context, not as
   permission to invent history.
7. Call `mcp__vps__analyze_report` with:
   ```text
   report_id = current report
   force = false
   ```
   The project AnalysisOrchestrator remains authoritative for exact reuse,
   assisted analysis, full analysis, Ollama calls, and persistence.
8. Call `mcp__vps__get_analysis` using the current `report_id`.
9. Require the returned analysis to belong to the current report.
10. Use persisted fields such as `analysis_source`, `reused_from_analysis_id`,
    `retrieval_strategy`, `retrieval_score`, and `llm_called` as the
    authoritative description of what actually happened.

Do not call `force: true` in the normal workflow.

## Branch semantics

```text
exact lookup matched
  -> AnalysisOrchestrator should persist/reuse analysis for current report
  -> no manual copy of historical analysis

no exact match
  -> retrieve at most top 3 similar reports
  -> AnalysisOrchestrator decides assisted vs full analysis

retrieval degraded
  -> still call AnalysisOrchestrator
  -> preserve retrieval warning in the skill result
```

## Failure behavior

Fatal:

```text
current report missing
analyze_report failed
current persisted analysis missing after analyze_report
analysis/report identity mismatch
```

Non-fatal but report explicitly:

```text
exact lookup unavailable
similar retrieval unavailable
no similar historical cases
```

## Stopping conditions

Stop only after a persisted current-report analysis is verified or a fatal
analysis failure occurs.

## Output contract

Return:

```text
status
report_id
analysis_id
health_status
analysis_source
reused_from_analysis_id
retrieval_strategy
retrieval_score
llm_called
exact_match_found
similar_context_count
retrieval_warning, when present
error_code/error_message, when failed
```

Do not fabricate analysis, retrieval, Evidence, or Knowledge identifiers.
