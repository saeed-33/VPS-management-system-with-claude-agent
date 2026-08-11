# Project Structure and File Responsibilities

This document is generated from the current checkout.

Regenerate with:

```powershell
uv run python tools/generate_project_structure.py
```

## Architectural flow

```text
Server / Monitoring Profile
        ↓
Monitoring execution
        ↓
Report
        ↓
Analysis
        ↓
Investigation Router
        ↓
LangGraph Coordinator
        ↓
Specialist loops + Policy + SSH diagnostic tools
        ↓
Evidence
        ↓
Cross-Specialist Correlation
        ↓
Final Diagnosis + Narrative
        ↓
Runtime Snapshot Persistence
        ↓
API / Administration UI
        ↓
Evaluation / Production Readiness Gate
```

## File-by-file inventory

### Repository root / configuration

- `.env` — Project asset.
- `.env.example` — Example environment variables for local/runtime configuration.
- `.gitignore` — Project asset.
- `.phase_4_20_docs_closeout_backup/20260811_095025/README.md` — Project documentation.
- `.phase_4_20_docs_closeout_backup/20260811_095025/docs/README.md` — Project documentation.
- `.python-version` — Project asset.
- `README.md` — Top-level project overview and startup guidance.
- `apply_phase_4_20_docs_closeout.py` — Python module containing `backup()`, `copy_payload()`, `append_section()`, `validate_python()`, `run_generator()`.
- `assets/fonts/NotoNaskhArabic-Regular.ttf` — Project asset.
- `payload/docs/roadmap/phase-4-20-closeout.md` — Project documentation.
- `payload/docs/testing/RUNTIME_SCENARIOS.md` — Project documentation.
- `payload/docs/testing/TESTING_STRATEGY.md` — Project documentation.
- `payload/docs/testing/TEST_CATALOG.md` — Project documentation.
- `payload/tools/generate_project_structure.py` — Python module containing `should_skip()`, `python_summary()`, `describe()`, `group()`, `main()`.
- `payload/tools/generate_test_catalog.py` — Python module containing `first_docstring()`, `test_functions()`, `main()`.
- `payload/tools/linux_scenarios/random_linux_workload.py` — Python module containing `now()`, `busy_worker()`, `cpu_scenario()`, `memory_scenario()`, `disk_io_scenario()`.
- `payload/tools/linux_scenarios/run_linux_scenario_matrix.py` — Python module containing `main()`.
- `payload/tools/run_all_tests.py` — Python module containing `run()`, `tool_exists()`, `main()`.
- `pyproject.toml` — Python project metadata and dependency configuration.
- `pytest.ini` — Pytest configuration.
- `reports/20260805T142639_b4b15481.json` — Structured configuration or generated data.
- `reports/20260805T142739_2d6ae7cf.json` — Structured configuration or generated data.
- `reports/20260805T142840_f9195f7b.json` — Structured configuration or generated data.
- `reports/20260805T142940_1d4b9436.json` — Structured configuration or generated data.
- `reports/20260805T143041_c87bb287.json` — Structured configuration or generated data.
- `reports/server_1/20260805T152916_15b684bf.json` — Structured configuration or generated data.
- `reports/server_1/20260805T153016_3afdc079.json` — Structured configuration or generated data.
- `reports/server_1/20260805T153117_686f62b7.json` — Structured configuration or generated data.
- `reports/server_2/20260805T152926_b063a281.json` — Structured configuration or generated data.
- `reports/server_3/20260805T153011_771e068b.json` — Structured configuration or generated data.
- `reports/server_3/20260805T153112_d417fe8b.json` — Structured configuration or generated data.
- `requirements-dev.txt` — Text data/documentation asset.
- `requirements.txt` — Text data/documentation asset.
- `uv.lock` — Project asset.

### Application core

- `app/.python-version` — Project asset.
- `app/__init__.py` — Python module.
- `app/bootstrap.py` — Application composition root / dependency container. Builds repositories, services, LLM clients, registries, Policy, coordinators, and shared runtime dependencies.
- `app/main.py` — FastAPI application entry point; registers API/web routers and startup/shutdown behavior.

### Administration API and Web UI

- `app/admin/__init__.py` — Administration interface package.
- `app/admin/api/__init__.py` — FastAPI API router/module.
- `app/admin/api/commands.py` — FastAPI API router/module exposing `list_commands()`, `get_command()`, `create_command()`, `update_command()`.
- `app/admin/api/diagnostic_tools.py` — FastAPI API router/module exposing `list_diagnostic_tools()`.
- `app/admin/api/investigations.py` — FastAPI API router/module exposing `list_investigations()`, `get_investigation()`, `list_report_investigations()`.
- `app/admin/api/knowledge_sources.py` — FastAPI API router/module exposing `list_knowledge_sources()`, `get_knowledge_source()`, `create_knowledge_source()`, `update_knowledge_source()`.
- `app/admin/api/profiles.py` — FastAPI API router/module exposing `list_profiles()`, `get_profile()`, `create_profile()`, `update_profile()`.
- `app/admin/api/reports.py` — FastAPI API router/module exposing `list_reports()`, `get_report()`, `get_report_analysis()`, `get_report_analysis_sources()`.
- `app/admin/api/servers.py` — FastAPI API router/module exposing `list_servers()`, `get_server()`, `create_server()`, `update_server()`.
- `app/admin/api/specialists.py` — FastAPI API router/module exposing `list_specialists()`, `get_specialist()`, `create_specialist()`, `update_specialist()`.
- `app/admin/dependencies.py` — Python module containing `get_monitoring_profile_service()`, `get_server_service()`, `get_command_service()`, `get_report_query_service()`, `get_ssh_test_service()`.
- `app/admin/schemas/__init__.py` — API/schema models.
- `app/admin/schemas/commands.py` — API/schema models including class `CommandCreateRequest`, class `CommandUpdateRequest`, class `CommandResponse`, class `AssignCommandRequest`, class `UpdateCommandAssignmentRequest`.
- `app/admin/schemas/investigations.py` — API/schema models including class `InvestigationCandidateResponse`, class `InvestigationSummaryResponse`, class `InvestigationRuntimeResponse`, class `InvestigationDetailResponse`.
- `app/admin/schemas/knowledge_sources.py` — API/schema models including class `KnowledgeSourceCreateRequest`, class `KnowledgeSourceUpdateRequest`, class `KnowledgeSourceEnabledRequest`, class `KnowledgeSourceResponse`.
- `app/admin/schemas/profiles.py` — API/schema models including class `MonitoringProfileCreateRequest`, class `MonitoringProfileUpdateRequest`, class `MonitoringProfileResponse`, class `AssignProfileCommandRequest`, class `UpdateProfileCommandRequest`.
- `app/admin/schemas/reports.py` — API/schema models including class `ReportListItemResponse`, class `PaginatedReportsResponse`, class `CommandExecutionResponse`, class `ReportDetailsResponse`, class `ReportAnalysisResponse`.
- `app/admin/schemas/servers.py` — API/schema models including class `ServerCreateRequest`, class `ServerUpdateRequest`, class `ServerResponse`, class `SSHTestResponse`.
- `app/admin/schemas/specialists.py` — API/schema models including class `SpecialistCreateRequest`, class `SpecialistUpdateRequest`, class `SpecialistEnabledRequest`, class `SpecialistResponse`.
- `app/admin/services/__init__.py` — Service-layer module.
- `app/admin/services/report_pdf_service.py` — Service-layer module containing class `ReportPdfService`.
- `app/admin/services/ssh_test_service.py` — Service-layer module containing class `SSHTestResult`, class `SSHTestService`.
- `app/admin/web/__init__.py` — Python module.
- `app/admin/web/routes.py` — Python module containing `dashboard_page()`, `servers_page()`, `commands_page()`, `investigations_page()`, `reports_page()`.
- `app/admin/web/static/css/app.css` — Administration UI stylesheet.
- `app/admin/web/static/js/app.js` — Administration UI browser-side JavaScript.
- `app/admin/web/templates/base.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/commands.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/dashboard.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/investigation_details.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/investigations.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/knowledge_sources.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/monitoring_profiles.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/report_details.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/reports.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/servers.html` — Jinja/HTML administration UI template.
- `app/admin/web/templates/specialists.html` — Jinja/HTML administration UI template.

### Agent / Analysis

- `app/agent/__init__.py` — Monitoring agent package.
- `app/agent/analysis/__init__.py` — Python module.
- `app/agent/analysis/__init__.py.__tmp` — Project asset.
- `app/agent/analysis/analysis_agent_manager.py` — Python module containing class `AnalysisAgentManager`.
- `app/agent/analysis/analysis_orchestrator.py` — Python module containing class `AnalysisOrchestrator`.
- `app/agent/analysis/client_factory.py` — Python module containing `create_llm_analysis_client()`.
- `app/agent/analysis/llm_client.py` — Python module containing class `LLMAnalysisClient`.
- `app/agent/analysis/ollama_client.py` — Python module containing class `OllamaAnalysisClient`.
- `app/agent/analysis/openai_client.py` — Python module containing class `OpenAIAnalysisClient`.
- `app/agent/analysis/prompts.py` — Python module containing `build_analysis_prompt()`.
- `app/agent/analysis/report_analyzer.py` — Python module containing class `ReportAnalyzer`.
- `app/agent/analysis/report_serializer.py` — Python module containing class `ReportSerializer`.
- `app/agent/analysis/retrieval/__init__.py` — Historical analysis retrieval components.
- `app/agent/analysis/retrieval/context_builder.py` — Python module containing class `RagContextBuilder`.
- `app/agent/analysis/retrieval/embedding_client.py` — Python module containing class `EmbeddingClient`.
- `app/agent/analysis/retrieval/embedding_factory.py` — Python module containing `create_embedding_client()`.
- `app/agent/analysis/retrieval/full_text_retriever.py` — Python module containing class `FullTextCandidate`, class `FullTextQueryBuilder`, class `FullTextRetriever`.
- `app/agent/analysis/retrieval/hybrid_retriever.py` — Python module containing class `_FusionCandidate`, class `HybridRetriever`.
- `app/agent/analysis/retrieval/ollama_embedding_client.py` — Python module containing class `OllamaEmbeddingClient`.
- `app/agent/analysis/retrieval/performance_profiler.py` — Python module containing class `PerformanceProfile`, `start_profile()`, `record_timing()`, `set_counter()`, `snapshot()`.
- `app/agent/analysis/retrieval/rag_context.py` — Python module containing class `RetrievedAnalysisContext`.
- `app/agent/analysis/retrieval/rag_retriever.py` — Python module containing class `RagRetriever`.
- `app/agent/analysis/retrieval/report_fingerprint.py` — Python module containing class `ReportFingerprintService`.
- `app/agent/analysis/retrieval/report_normalizer.py` — Python module containing class `ReportNormalizer`.
- `app/agent/analysis/retrieval/retrieval_indexer.py` — Python module containing class `RetrievalIndexer`.
- `app/agent/analysis/retrieval/reuse_policy.py` — Python module containing class `AnalysisDecision`, class `AnalysisDecisionResult`, class `AnalysisReusePolicy`.
- `app/agent/analysis/retrieval/structured_compatibility.py` — Python module containing class `CompatibilityConflict`, class `CompatibilityResult`, class `StructuredCompatibilityChecker`.
- `app/agent/analysis/server_analysis_agent.py` — Python module containing class `AnalysisJob`, class `ServerAnalysisAgent`.
- `app/agent/graph/__init__.py` — LangGraph workflow for monitoring cycles.
- `app/agent/graph/monitoring_graph.py` — Python module containing `build_monitoring_graph()`.
- `app/agent/graph/state.py` — Python module containing class `MonitoringGraphState`.
- `app/agent/monitoring_service.py` — Python module containing class `ServerRecord`, class `MonitoringCommandRecord`, class `ServerRepositoryProtocol`, class `MonitoringProfileRepositoryProtocol`, class `ReportRepositoryProtocol`.
- `app/agent/report_service.py` — Python module containing class `ReportService`.
- `app/agent/scheduler.py` — Python module containing class `SchedulableServerRecord`, class `SchedulerServerRepositoryProtocol`, class `MonitoringScheduler`.
- `app/agent/ssh/__init__.py` — SSH infrastructure used by the monitoring agent.
- `app/agent/ssh/client.py` — Python module containing class `SSHConnectionConfig`, class `SSHClient`.
- `app/agent/ssh/command_executor.py` — Python module containing class `CommandExecutionResult`, class `SSHCommandExecutor`.

### Autonomous Investigation

- `app/agent/investigation/__init__.py` — Autonomous Investigation subsystem module.
- `app/agent/investigation/contracts.py` — Autonomous Investigation subsystem module containing class `InvestigationStatus`, class `SpecialistTaskStatus`, class `EvidenceKind`, class `KnowledgeSourceType`, class `InvestigationBudget`.
- `app/agent/investigation/correlation.py` — Autonomous Investigation subsystem module containing class `DiagnosisCertainty`, class `DiagnosisConflict`, class `CorrelatedDiagnosisClaim`, class `FinalDiagnosis`, class `CrossSpecialistCorrelator`.
- `app/agent/investigation/diagnostic_policy.py` — Autonomous Investigation subsystem module containing class `DiagnosticPolicyDecision`, class `DiagnosticPolicyReason`, class `DiagnosticPolicyRequest`, class `DiagnosticPolicyResult`, class `DiagnosticPolicyEngine`.
- `app/agent/investigation/diagnostic_tools.py` — Autonomous Investigation subsystem module containing class `DiagnosticToolRisk`, class `DiagnosticParameterKind`, class `DiagnosticToolParameter`, class `DiagnosticToolDefinition`, class `DiagnosticToolCall`.
- `app/agent/investigation/evidence_collection.py` — Autonomous Investigation subsystem module containing class `DiagnosticExecutionOutcome`, class `DiagnosticCommandRunner`, class `ServerRecord`, class `ServerRepositoryProtocol`, class `EvidenceCollectionRequest`.
- `app/agent/investigation/final_diagnosis_synthesizer.py` — Autonomous Investigation subsystem module containing class `FinalDiagnosisNarrativeOutput`, class `FinalDiagnosisNarrative`, class `FinalDiagnosisNarrativeClient`, class `OllamaFinalDiagnosisNarrativeClient`, class `OpenAIFinalDiagnosisNarrativeClient`.
- `app/agent/investigation/investigation_router.py` — Autonomous Investigation subsystem module containing class `RoutingReason`, class `SpecialistRoutingMatch`, class `InvestigationRoutingDecision`, class `_IssueSignal`, class `_Candidate`.
- `app/agent/investigation/knowledge_chunker.py` — Autonomous Investigation subsystem module containing class `KnowledgeChunkerConfig`, class `_Block`, class `StructureAwareKnowledgeChunker`.
- `app/agent/investigation/knowledge_chunking_service.py` — Autonomous Investigation subsystem module containing class `KnowledgeChunkingService`.
- `app/agent/investigation/knowledge_indexer.py` — Autonomous Investigation subsystem module containing class `KnowledgeIndexingResult`, class `KnowledgeIndexer`.
- `app/agent/investigation/knowledge_ingestion_contracts.py` — Autonomous Investigation subsystem module containing class `KnowledgeDocumentStatus`, class `ParsedKnowledgeDocument`, class `KnowledgeChunkDraft`.
- `app/agent/investigation/knowledge_ingestion_service.py` — Autonomous Investigation subsystem module containing class `KnowledgeIngestionService`.
- `app/agent/investigation/knowledge_parsers.py` — Autonomous Investigation subsystem module containing `normalize_text()`, class `_HTMLTextExtractor`, class `KnowledgeContentParser`.
- `app/agent/investigation/knowledge_retrieval.py` — Autonomous Investigation subsystem module containing class `KnowledgeRetrievalContext`, class `_FusionCandidate`, class `KnowledgeHybridRetriever`.
- `app/agent/investigation/knowledge_source_loader.py` — Autonomous Investigation subsystem module containing class `LoadedKnowledgeContent`, class `KnowledgeSourceLoader`.
- `app/agent/investigation/knowledge_source_registry.py` — Autonomous Investigation subsystem module containing class `KnowledgeSourceRuntimeDefinition`, class `KnowledgeSourceRegistrySnapshot`, class `KnowledgeSourceRegistry`.
- `app/agent/investigation/langgraph_orchestrator.py` — Autonomous Investigation subsystem module containing class `SpecialistWorkerAssignment`, class `InvestigationGraphState`, class `SpecialistWorkerState`, class `LangGraphServerCoordinator`.
- `app/agent/investigation/langgraph_secondary_orchestrator.py` — Autonomous Investigation subsystem module containing class `SecondaryRecommendationDecision`, class `SecondaryInvestigationGraphState`, class `DynamicSecondaryLangGraphCoordinator`.
- `app/agent/investigation/persistence_service.py` — Autonomous Investigation subsystem module containing class `InvestigationPersistenceService`.
- `app/agent/investigation/runtime_snapshot_service.py` — Autonomous Investigation subsystem module containing class `InvestigationRuntimeSnapshotService`.
- `app/agent/investigation/server_coordinator.py` — Autonomous Investigation subsystem module containing class `ServerCoordinatorSpecialistRun`, class `ServerCoordinatorResult`, class `ServerCoordinator`.
- `app/agent/investigation/specialist_context.py` — Autonomous Investigation subsystem module containing class `SpecialistContextBudget`, class `SpecialistContextSnapshot`, class `SpecialistKnowledgeQueryBuilder`, class `SpecialistContextBuilder`.
- `app/agent/investigation/specialist_investigation_loop.py` — Autonomous Investigation subsystem module containing class `SpecialistLoopStopReason`, class `SpecialistLoopToolDecision`, class `SpecialistLoopRoundTrace`, class `SpecialistInvestigationLoopResult`, class `SpecialistInvestigationLoop`.
- `app/agent/investigation/specialist_reasoning_agent.py` — Autonomous Investigation subsystem module containing class `SpecialistDiagnosticToolRequest`, class `SpecialistReasoningExecution`, class `SpecialistReasoningAgent`.
- `app/agent/investigation/specialist_reasoning_client.py` — Autonomous Investigation subsystem module containing class `SpecialistReasoningClient`, class `OllamaSpecialistReasoningClient`, class `OpenAISpecialistReasoningClient`, `create_specialist_reasoning_client()`.
- `app/agent/investigation/specialist_registry.py` — Autonomous Investigation subsystem module containing class `SpecialistRegistryValidationError`, class `SpecialistRuntimeDefinition`, class `SpecialistDomainMatch`, class `SpecialistRegistrySnapshot`, class `SpecialistRegistry`.

### Evaluation and Production Readiness

- `app/agent/evaluation/__init__.py` — Phase 4.20 evaluation/readiness component.
- `app/agent/evaluation/aggregate_readiness.py` — Phase 4.20 evaluation/readiness component containing class `AggregateEvaluationResult`, class `AggregateReadinessEvaluator`.
- `app/agent/evaluation/cases.py` — Phase 4.20 evaluation/readiness component containing class `EvaluationCase`, `default_evaluation_cases()`.
- `app/agent/evaluation/contracts.py` — Phase 4.20 evaluation/readiness component containing class `EvaluationMetric`, class `ReadinessStatus`, class `EvaluationObservation`, class `MetricThreshold`, class `MetricEvaluation`.
- `app/agent/evaluation/persisted_runtime.py` — Phase 4.20 evaluation/readiness component containing class `PersistedRuntimeEvaluation`, class `PersistedRuntimeEvaluator`.
- `app/agent/evaluation/readiness_gate.py` — Phase 4.20 evaluation/readiness component containing class `ProductionReadinessGate`.
- `app/agent/evaluation/runner.py` — Phase 4.20 evaluation/readiness component containing class `EvaluationCaseResult`, class `EvaluationRunResult`, class `DeterministicEvaluationRunner`, `expected_behavior_executor()`.
- `app/agent/evaluation/safety_runtime.py` — Phase 4.20 evaluation/readiness component containing class `_StaticRegistry`, `evaluate_routing_cases()`, `evaluate_policy_cases()`, `evaluate_provider_cases()`, `evaluate_safety_runtime()`.

### Shared application layer

- `app/shared/__init__.py` — Shared application components.
- `app/shared/config.py` — Environment-backed application configuration.
- `app/shared/database/__init__.py` — Python module.
- `app/shared/database/base.py` — Python module containing class `Base`.
- `app/shared/database/engine.py` — Python module containing `create_database_tables()`.
- `app/shared/database/migrations/step_3_10_performance_metrics.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_3_3_full_text_search.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_3_7_hnsw_vector_search.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_3_7_verify_hnsw.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_4_2_specialist_definitions.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_4_6_investigation_persistence.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_4_7_knowledge_sources.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_4_8_0_knowledge_rag_schema.sql` — Database migration/configuration asset.
- `app/shared/database/migrations/step_4_8_3_knowledge_indexes.sql` — Database migration/configuration asset.
- `app/shared/database/models/__init__.py` — Python module.
- `app/shared/database/models/command_execution.py` — Python module containing class `CommandExecutionModel`.
- `app/shared/database/models/investigation.py` — Python module containing class `InvestigationModel`, class `InvestigationSpecialistCandidateModel`.
- `app/shared/database/models/knowledge_document.py` — Python module containing class `KnowledgeDocumentModel`, class `KnowledgeChunkModel`.
- `app/shared/database/models/knowledge_source.py` — Python module containing class `KnowledgeSourceModel`.
- `app/shared/database/models/monitor_command.py` — Python module containing class `MonitorCommandModel`.
- `app/shared/database/models/monitoring_profile.py` — Python module containing class `MonitoringProfileModel`.
- `app/shared/database/models/monitoring_report.py` — Python module containing class `MonitoringReportModel`.
- `app/shared/database/models/profile_command.py` — Python module containing class `MonitoringProfileCommandModel`.
- `app/shared/database/models/report_analysis.py` — Python module containing class `AnalysisJobStatus`, class `ReportAnalysisModel`.
- `app/shared/database/models/report_analysis_source.py` — Python module containing class `ReportAnalysisSourceModel`.
- `app/shared/database/models/report_retrieval_document.py` — Python module containing class `ReportRetrievalDocumentModel`.
- `app/shared/database/models/server.py` — Python module containing class `ServerStatus`, class `ServerModel`.
- `app/shared/database/models/specialist_definition.py` — Python module containing class `SpecialistDefinitionModel`.
- `app/shared/database/repositories/__init__.py` — Persistence repository module.
- `app/shared/database/repositories/analysis_repository.py` — Persistence repository module containing class `AnalysisRepository`.
- `app/shared/database/repositories/analysis_source_repository.py` — Persistence repository module containing class `AnalysisSourceRepository`.
- `app/shared/database/repositories/command_repository.py` — Persistence repository module containing class `CommandRepository`.
- `app/shared/database/repositories/investigation_repository.py` — Persistence repository module containing class `InvestigationRepository`.
- `app/shared/database/repositories/knowledge_document_repository.py` — Persistence repository module containing class `KnowledgeDocumentRepository`.
- `app/shared/database/repositories/knowledge_retrieval_repository.py` — Persistence repository module containing class `KnowledgeSearchRow`, class `KnowledgeRetrievalRepository`.
- `app/shared/database/repositories/knowledge_source_repository.py` — Persistence repository module containing class `KnowledgeSourceRepository`.
- `app/shared/database/repositories/profile_repository.py` — Persistence repository module containing class `MonitoringProfileRepository`.
- `app/shared/database/repositories/report_repository.py` — Persistence repository module containing class `ReportRepository`.
- `app/shared/database/repositories/retrieval_repository.py` — Persistence repository module containing class `RetrievalRepository`.
- `app/shared/database/repositories/server_repository.py` — Persistence repository module containing class `ServerRepository`.
- `app/shared/database/repositories/specialist_definition_repository.py` — Persistence repository module containing class `SpecialistDefinitionRepository`.
- `app/shared/database/session.py` — Python module containing `get_database_session()`.
- `app/shared/dto/__init__.py` — Python module.
- `app/shared/dto/analysis.py` — Python module containing class `AnalysisHealthStatus`, class `AnalysisSeverity`, class `AnalysisIssue`, class `ReportAnalysisResult`, class `StoredReportAnalysis`.
- `app/shared/dto/commands.py` — Python module containing class `CreateCommandDTO`, class `UpdateCommandDTO`, class `CommandExecutionConfig`.
- `app/shared/dto/investigation_read_models.py` — Python module containing class `InvestigationCandidateReadModel`, class `InvestigationSummaryReadModel`, class `InvestigationRuntimeReadModel`, class `InvestigationDetailReadModel`.
- `app/shared/dto/investigations.py` — Python module containing class `PersistInvestigationCandidateDTO`, class `PersistInvestigationDTO`.
- `app/shared/dto/knowledge_sources.py` — Python module containing class `CreateKnowledgeSourceDTO`, class `UpdateKnowledgeSourceDTO`.
- `app/shared/dto/profiles.py` — Python module containing class `CreateMonitoringProfileDTO`, class `UpdateMonitoringProfileDTO`, class `MonitoringProfileCommandConfig`.
- `app/shared/dto/reports.py` — Python module containing class `MonitoringReportStatus`, class `CommandExecutionData`, class `MonitoringReportData`, class `CommandExecutionDTO`, class `ReportListItemDTO`.
- `app/shared/dto/servers.py` — Python module containing class `CreateServerDTO`, class `UpdateServerDTO`.
- `app/shared/dto/specialist_reasoning.py` — Python module containing class `SpecialistFindingOutput`, class `SpecialistHypothesisOutput`, class `SpecialistDiagnosticToolRequestOutput`, class `SpecialistReasoningOutput`, class `SpecialistFinalSynthesisOutput`.
- `app/shared/dto/specialists.py` — Python module containing `validate_specialist_slug()`, class `CreateSpecialistDefinitionDTO`, class `UpdateSpecialistDefinitionDTO`.
- `app/shared/enums/fingerprint_strategy.py` — Python module containing class `FingerprintStrategy`.
- `app/shared/exceptions.py` — Python module containing class `ApplicationError`, class `EntityNotFoundError`, class `ServerNotFoundError`, class `CommandNotFoundError`, class `ReportNotFoundError`.
- `app/shared/logging.py` — Python module containing `configure_logging()`.
- `app/shared/services/__init__.py` — Service-layer module.
- `app/shared/services/command_service.py` — Service-layer module containing class `CommandService`.
- `app/shared/services/investigation_read_service.py` — Service-layer module containing class `InvestigationReadService`.
- `app/shared/services/knowledge_source_service.py` — Service-layer module containing class `KnowledgeSourceService`.
- `app/shared/services/profile_service.py` — Service-layer module containing class `MonitoringProfileService`.
- `app/shared/services/report_service.py` — Service-layer module containing class `ReportQueryService`.
- `app/shared/services/server_service.py` — Service-layer module containing class `ServerService`.
- `app/shared/services/specialist_service.py` — Service-layer module containing class `SpecialistDefinitionService`.
- `app/shared/utils/__init__.py` — Python module.
- `app/shared/utils/datetime.py` — Python module containing `utc_now()`.
- `app/shared/utils/filesystem.py` — Python module.
- `app/shared/utils/ids.py` — Python module.

### Tools and acceptance scripts

- `tools/bootstrap_database.py` — Operator/developer tool exposing `connection_kwargs()`, `database_exists()`, `create_database_if_missing()`, `ensure_vector_extension()`.
- `tools/check_knowledge_source_acceptance.py` — Operator/developer tool exposing `main()`.
- `tools/chunk_knowledge_document.py` — Operator/developer tool exposing `main()`.
- `tools/collect_diagnostic_evidence.py` — Operator/developer tool exposing `parse_args()`, `run()`, `main()`.
- `tools/evaluate_rag.py` — Operator/developer tool exposing class `EvaluationSummary`, `ratio()`, `fetch_hnsw_index_present()`, `build_document_map()`.
- `tools/generate_project_structure.py` — Operator/developer tool exposing `should_skip()`, `python_summary()`, `describe()`, `group()`.
- `tools/generate_test_catalog.py` — Operator/developer tool exposing `first_docstring()`, `test_functions()`, `main()`.
- `tools/index_knowledge_document.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/ingest_knowledge_source.py` — Operator/developer tool exposing `main()`.
- `tools/inspect_diagnostic_policy.py` — Operator/developer tool exposing `main()`.
- `tools/inspect_diagnostic_tools.py` — Operator/developer tool exposing `main()`.
- `tools/inspect_investigation.py` — Operator/developer tool exposing `main()`.
- `tools/inspect_investigation_routing.py` — Operator/developer tool exposing `print_matches()`, `main()`.
- `tools/inspect_knowledge_index.py` — Operator/developer tool exposing `db_indexes()`, `main()`.
- `tools/inspect_knowledge_sources.py` — Operator/developer tool exposing `main()`.
- `tools/inspect_specialist_context.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/inspect_specialist_registry.py` — Operator/developer tool exposing `main()`.
- `tools/linux_scenarios/random_linux_workload.py` — Operator/developer tool exposing `now()`, `busy_worker()`, `cpu_scenario()`, `memory_scenario()`.
- `tools/linux_scenarios/run_linux_scenario_matrix.py` — Operator/developer tool exposing `main()`.
- `tools/list_routes.py` — Operator/developer tool exposing `collect_routes()`, `main()`.
- `tools/persist_investigation_routing.py` — Operator/developer tool exposing `main()`.
- `tools/production_preflight.py` — Operator/developer tool exposing `check()`, `main()`.
- `tools/reason_specialist_context.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/report_rag_performance.py` — Operator/developer tool exposing `percentile()`, `stats()`, `main()`.
- `tools/run_all_tests.py` — Operator/developer tool exposing `run()`, `tool_exists()`, `main()`.
- `tools/run_correlation_acceptance.py` — Operator/developer tool exposing class `ControlledRecommendationParallelCoordinator`, `normalize_issues()`, `specialist_by_slug()`, `controlled_initial_decision()`.
- `tools/run_evaluation_dataset.py` — Operator/developer tool exposing `main()`.
- `tools/run_final_diagnosis_acceptance.py` — Operator/developer tool exposing class `ControlledRecommendationParallelCoordinator`, `normalize_issues()`, `specialist_by_slug()`, `controlled_initial_decision()`.
- `tools/run_investigation_web_api_acceptance.py` — Operator/developer tool exposing `status()`, `main()`.
- `tools/run_langgraph_controlled_secondary_acceptance.py` — Operator/developer tool exposing class `ControlledRecommendationParallelCoordinator`, `normalize_issues()`, `specialist_by_slug()`, `controlled_initial_decision()`.
- `tools/run_langgraph_coordinator_acceptance.py` — Operator/developer tool exposing `normalize_issues()`, `run()`, `main()`.
- `tools/run_langgraph_parallel_acceptance.py` — Operator/developer tool exposing `normalize_issues()`, `controlled_decision()`, `run()`, `main()`.
- `tools/run_langgraph_secondary_acceptance.py` — Operator/developer tool exposing `normalize_issues()`, `controlled_initial_decision()`, `run()`, `main()`.
- `tools/run_persisted_runtime_acceptance.py` — Operator/developer tool exposing `normalize_issues()`, `controlled_parallel_decision()`, `choose_runtime_evidence()`, `inject_controlled_conflict_findings()`.
- `tools/run_persisted_runtime_evaluation.py` — Operator/developer tool exposing `main()`.
- `tools/run_production_readiness_evaluation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/run_runtime_sample_expansion.py` — Operator/developer tool exposing `normalize_issues()`, `controlled_parallel_decision()`, `choose_runtime_evidence()`, `inject_controlled_conflict()`.
- `tools/run_safety_runtime_evaluation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/run_server_coordinator_acceptance.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/run_specialist_investigation.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/search_knowledge.py` — Operator/developer tool exposing `run()`, `main()`.
- `tools/seed_knowledge_sources.py` — Operator/developer tool exposing class `SeedKnowledgeSource`, `create_dto()`, `update_dto()`, `main()`.
- `tools/seed_specialists.py` — Operator/developer tool exposing `build_create_dto()`, `build_update_dto()`, `main()`.

### Tests

- `tests/conftest.py` — Pytest coverage for the corresponding project behavior.
- `tests/test_aggregate_readiness.py` — Pytest coverage for `obs()`, `test_aggregate_combines_sources()`, `test_sample_deficits_are_reported()`, `test_one_real_runtime_sample_is_not_ready()`, `test_hard_failure_blocks_when_samples_sufficient()`.
- `tests/test_cross_specialist_conflicts.py` — Pytest coverage for `make_state()`, `make_run()`, `wrap()`, `test_explicit_conflicting_states_become_unknown()`, `test_matching_explicit_states_do_not_conflict()`.
- `tests/test_cross_specialist_correlation.py` — Pytest coverage for `make_state()`, `make_run()`, `wrap()`, `test_live_evidence_high_confidence_is_confirmed()`, `test_live_evidence_lower_confidence_is_probable()`.
- `tests/test_diagnostic_policy.py` — Pytest coverage for `specialist()`, `request()`, `engine()`, `test_policy_allows_registered_assigned_safe_tool()`, `test_policy_denies_unknown_tool()`.
- `tests/test_diagnostic_tool_registry.py` — Pytest coverage for `registry()`, `test_default_registry_contains_expected_read_only_tools()`, `test_service_parameter_rejects_shell_injection()`, `test_path_parameter_rejects_shell_injection()`, `test_connect_probe_validates_port()`.
- `tests/test_diagnostic_tools_api.py` — Pytest coverage for `test_diagnostic_tools_api_lists_registry()`.
- `tests/test_evaluation_dataset_runner.py` — Pytest coverage for `test_default_dataset_meets_gate_sample_counts()`, `test_case_ids_are_unique()`, `test_expected_behavior_executor_wires_gate()`, `test_runtime_failure_blocks_hard_metric()`, `test_executor_must_return_matching_case_id()`.
- `tests/test_evidence_collection.py` — Pytest coverage for class `Repository`, class `Runner`, `make_outcome()`, `allowed_policy()`, `denied_policy()`.
- `tests/test_final_diagnosis_synthesizer.py` — Pytest coverage for `diagnosis()`, class `Client`, `test_valid_llm_narrative_is_used()`, `test_unknown_claim_id_uses_fallback()`, `test_conflict_must_be_preserved()`.
- `tests/test_hybrid_retriever.py` — Pytest coverage for class `FakeAnalysis`, class `FakeDocument`, class `FakeAnalysisRepository`, class `FakeRetrievalRepository`, class `FakeVectorRetriever`.
- `tests/test_investigation_contracts.py` — Pytest coverage for `make_state()`, `make_task()`, `test_default_investigation_state()`, `test_confidence_must_be_normalized()`, `test_duplicate_evidence_is_rejected()`.
- `tests/test_investigation_persistence_service.py` — Pytest coverage for class `FakeRepository`, `make_match()`, `test_persistence_preserves_candidate_and_selected_ranks()`, `test_healthy_decision_can_be_persisted_for_audit()`.
- `tests/test_investigation_read_service.py` — Pytest coverage for class `Candidate`, class `Model`, class `Repository`, `test_read_model_does_not_invent_runtime()`, `test_runtime_snapshot_is_exposed_when_persisted()`.
- `tests/test_investigation_router.py` — Pytest coverage for `specialist()`, class `FakeRepository`, `make_router()`, `report()`, `analysis()`.
- `tests/test_investigation_runtime_snapshot_service.py` — Pytest coverage for class `Repository`, `make_result()`, `make_diagnosis()`, `test_build_snapshot_serializes_runtime()`, `test_persist_preserves_existing_metadata()`.
- `tests/test_investigations_api.py` — Pytest coverage for `summary()`, `detail()`, class `Service`, `make_client()`, `test_list_investigations()`.
- `tests/test_investigations_web.py` — Pytest coverage for `make_client()`, `test_investigations_page_is_available()`, `test_investigation_detail_page_is_available()`.
- `tests/test_knowledge_chunker.py` — Pytest coverage for `make_chunker()`, `test_markdown_heading_is_preserved_as_section()`, `test_html_heading_metadata_is_used()`, `test_pdf_page_metadata_preserves_page_number()`, `test_large_document_is_split_under_max_chars()`.
- `tests/test_knowledge_chunking_service.py` — Pytest coverage for class `Repository`, `test_chunking_service_persists_chunks()`.
- `tests/test_knowledge_hybrid_retrieval.py` — Pytest coverage for class `EmbeddingClient`, `row()`, class `Repository`, `test_hybrid_retrieval_fuses_both_branches()`, `test_specialist_scope_boosts_direct_source()`.
- `tests/test_knowledge_indexer.py` — Pytest coverage for class `EmbeddingClient`, class `Repository`, `test_indexer_embeds_all_chunks_and_marks_document()`, `test_indexer_skips_current_embedding()`, `test_force_reindexes_current_embedding()`.
- `tests/test_knowledge_ingestion_contracts.py` — Pytest coverage for `test_document_status_lifecycle_is_explicit()`, `test_parsed_document_requires_text()`, `test_parsed_document_accepts_large_document_metadata()`, `test_chunk_draft_preserves_page_and_section()`, `test_chunk_index_is_zero_based()`.
- `tests/test_knowledge_ingestion_service.py` — Pytest coverage for class `SourceRepository`, class `Loader`, class `DocumentRepository`, `test_ingestion_persists_parsed_document()`.
- `tests/test_knowledge_parsers.py` — Pytest coverage for `test_normalize_text_collapses_spacing()`, `test_html_parser_removes_script_and_extracts_title()`, `test_plain_text_parser()`.
- `tests/test_knowledge_retrieval_scope.py` — Pytest coverage for `compile_condition()`, `test_scope_condition_contains_specialist()`, `test_scope_condition_accepts_domains()`, `test_empty_scope_is_true()`.
- `tests/test_knowledge_source_foundation.py` — Pytest coverage for class `FakeRepository`, `source()`, `test_url_source_requires_uri()`, `test_inline_source_requires_content()`, `test_create_dto_normalizes_scope()`.
- `tests/test_knowledge_source_loader.py` — Pytest coverage for `test_inline_loader()`, `test_loader_rejects_unknown_source_type()`.
- `tests/test_knowledge_source_seed.py` — Pytest coverage for `test_seed_slugs_are_unique()`, `test_seed_sources_are_official_https_urls()`, `test_seed_covers_all_baseline_specialists()`, `test_each_seed_has_routing_scope()`.
- `tests/test_langgraph_orchestrator.py` — Pytest coverage for `specialist()`, class `Registry`, class `LoopOutput`, class `ParallelLoop`, `decision()`.
- `tests/test_langgraph_secondary_orchestrator.py` — Pytest coverage for `definition()`, class `Registry`, class `FakeLoopResult`, class `ParallelCoordinator`, `decision()`.
- `tests/test_ollama_context_window.py` — Pytest coverage for `run_request()`, `test_normal_reasoning_uses_32k_context_and_6144_output()`, `test_final_synthesis_uses_32k_context_and_6144_output()`.
- `tests/test_ollama_final_synthesis_dto.py` — Pytest coverage for `test_final_synthesis_minimal_contract_succeeds()`.
- `tests/test_ollama_final_synthesis_minimal_contract.py` — Pytest coverage for `test_final_synthesis_uses_minimal_json_mode()`, `test_normal_reasoning_keeps_existing_generation_limits()`.
- `tests/test_ollama_specialist_reasoning_client.py` — Pytest coverage for `make_response()`, `test_schema_rejection_is_cached_and_json_fallback_succeeds()`, `test_length_retry_uses_compact_retry_instruction()`, `test_final_synthesis_enables_provider_compact_mode()`.
- `tests/test_persisted_runtime_evaluation.py` — Pytest coverage for `make_detail()`, `by_metric()`, `test_valid_snapshot_emits_five_real_metrics()`, `test_unknown_evidence_fails_grounding()`, `test_budget_overrun_fails()`.
- `tests/test_production_readiness_gate.py` — Pytest coverage for `observations_for_thresholds()`, `test_gate_requires_minimum_samples()`, `test_all_thresholds_pass_supervised_only()`, `test_hard_safety_failure_blocks()`, `test_policy_failure_blocks()`.
- `tests/test_rag_evaluation_contract.py` — Pytest coverage for `test_hybrid_does_not_use_rrf_as_vector_similarity()`, `test_orchestrator_persists_vector_similarity_not_rrf()`, `test_vector_repository_filters_before_limit()`.
- `tests/test_reuse_policy.py` — Pytest coverage for `policy()`, `test_exact_fingerprint_reuses_analysis()`, `test_force_always_requires_full_analysis()`, `test_compatible_historical_context_is_assisted()`, `test_context_is_ignored_when_assisted_is_disabled()`.
- `tests/test_route_inventory.py` — Pytest coverage for `test_route_inventory_contains_application_routes()`, `test_web_routes_are_excluded_from_openapi()`, `test_specialists_api_is_in_openapi_inventory()`, `test_health_route_remains_visible()`.
- `tests/test_safety_runtime_evaluation.py` — Pytest coverage for `test_routing_runtime_emits_ten_passes()`, `test_policy_runtime_emits_ten_passes()`, `test_provider_runtime_emits_ten_safe_results()`.
- `tests/test_server_coordinator.py` — Pytest coverage for `specialist()`, class `Registry`, class `LoopOutput`, class `Loop`, `decision()`.
- `tests/test_server_coordinator_initial_evidence.py` — Pytest coverage for `test_initial_connection_failure_becomes_citable_analysis_evidence()`, `test_empty_initial_analysis_produces_no_evidence()`.
- `tests/test_specialist_context.py` — Pytest coverage for `specialist()`, `task()`, `knowledge()`, class `Retriever`, `test_context_preserves_knowledge_source_ids()`.
- `tests/test_specialist_definition_repository.py` — Pytest coverage for `repository()`, `make_specialist()`, `test_create_and_reload()`, `test_slug_is_normalized()`, `test_duplicate_slug_is_rejected()`.
- `tests/test_specialist_investigation_loop.py` — Pytest coverage for class `ContextBuilder`, class `ReasoningAgent`, class `EvidenceCollector`, `specialist()`, `task()`.
- `tests/test_specialist_reasoning_agent.py` — Pytest coverage for class `Client`, `context()`, `valid_output()`, `test_reasoning_converts_valid_output_to_contract()`, `test_unknown_knowledge_citation_is_rejected()`.
- `tests/test_specialist_reasoning_client_ollama_compat.py` — Pytest coverage for class `FakeResponse`, class `FakeHTTPClient`, `valid_content()`, `make_client()`, `test_schema_http_400_falls_back_to_json_mode()`.
- `tests/test_specialist_reasoning_client_structured_output.py` — Pytest coverage for class `Response`, class `HTTPClient`, `valid_content()`, `make_client()`, `test_ollama_uses_json_schema_as_format()`.
- `tests/test_specialist_reasoning_objective_prompt.py` — Pytest coverage for class `Client`, `context()`, `test_objective_is_prominent_before_and_after_catalog()`.
- `tests/test_specialist_reasoning_provenance_ids.py` — Pytest coverage for class `Client`, `context()`, `test_evidence_namespace_prefix_is_normalized_only_for_real_id()`, `test_unknown_prefixed_reference_remains_rejected()`.
- `tests/test_specialist_reasoning_tool_requests.py` — Pytest coverage for class `Client`, `context()`, `test_reasoning_returns_structured_tool_requests()`.
- `tests/test_specialist_registry.py` — Pytest coverage for `specialist()`, class `FakeRepository`, `test_disabled_specialists_are_excluded()`, `test_snapshot_is_stable_and_uses_one_repository_read()`, `test_registry_order_is_deterministic()`.
- `tests/test_specialists_api.py` — Pytest coverage for `model()`, class `FakeService`, `client()`, `test_list_specialists()`, `test_create_specialist()`.
- `tests/test_structured_compatibility.py` — Pytest coverage for `report()`, `test_identical_structured_state_is_compatible()`, `test_connection_state_conflict_is_rejected()`, `test_command_success_conflict_is_rejected()`, `test_exit_status_class_conflict_is_rejected()`.

### Documentation

- `docs/README.md` — Project documentation.
- `docs/api/admin-management.md` — Project documentation.
- `docs/api/admin-web-ui.md` — Project documentation.
- `docs/api/http-api.md` — Project documentation.
- `docs/api/investigations.md` — Project documentation.
- `docs/api/specialists-api.md` — Project documentation.
- `docs/architecture/aggregate-production-readiness.md` — Project documentation.
- `docs/architecture/cross-specialist-correlation.md` — Project documentation.
- `docs/architecture/database.md` — Project documentation.
- `docs/architecture/diagnostic-policy.md` — Project documentation.
- `docs/architecture/diagnostic-tool-registry.md` — Project documentation.
- `docs/architecture/dynamic-secondary-specialist-routing.md` — Project documentation.
- `docs/architecture/evaluation-dataset-runner.md` — Project documentation.
- `docs/architecture/evidence-collection.md` — Project documentation.
- `docs/architecture/investigation-contracts.md` — Project documentation.
- `docs/architecture/investigation-persistence.md` — Project documentation.
- `docs/architecture/investigation-read-models.md` — Project documentation.
- `docs/architecture/investigation-router.md` — Project documentation.
- `docs/architecture/investigation-runtime-snapshot.md` — Project documentation.
- `docs/architecture/knowledge-chunking.md` — Project documentation.
- `docs/architecture/knowledge-indexing.md` — Project documentation.
- `docs/architecture/knowledge-ingestion.md` — Project documentation.
- `docs/architecture/knowledge-rag-schema.md` — Project documentation.
- `docs/architecture/knowledge-retrieval.md` — Project documentation.
- `docs/architecture/knowledge-sources-seed.md` — Project documentation.
- `docs/architecture/knowledge-sources.md` — Project documentation.
- `docs/architecture/langgraph-investigation-orchestration.md` — Project documentation.
- `docs/architecture/overview.md` — Project documentation.
- `docs/architecture/persisted-runtime-evaluation.md` — Project documentation.
- `docs/architecture/production-readiness-gate.md` — Project documentation.
- `docs/architecture/runtime-sample-expansion.md` — Project documentation.
- `docs/architecture/safety-failure-injection.md` — Project documentation.
- `docs/architecture/server-coordinator.md` — Project documentation.
- `docs/architecture/specialist-context-builder.md` — Project documentation.
- `docs/architecture/specialist-definitions.md` — Project documentation.
- `docs/architecture/specialist-investigation-loop.md` — Project documentation.
- `docs/architecture/specialist-reasoning-agent.md` — Project documentation.
- `docs/architecture/specialist-registry.md` — Project documentation.
- `docs/decisions/ADR-008-dynamic-specialists.md` — Project documentation.
- `docs/decisions/ADR-009-hierarchical-investigation.md` — Project documentation.
- `docs/decisions/ADR-010-langgraph-orchestration-boundary.md` — Project documentation.
- `docs/decisions/ADR-011-dual-rag-and-knowledge-retrieval.md` — Project documentation.
- `docs/decisions/ADR-012-specialist-reasoning-and-provenance-boundary.md` — Project documentation.
- `docs/decisions/ADR-013-registered-read-only-diagnostic-tools.md` — Project documentation.
- `docs/decisions/ADR-014-langgraph-investigation-orchestration.md` — Project documentation.
- `docs/decisions/ADR-015-dynamic-secondary-specialist-routing.md` — Project documentation.
- `docs/decisions/README.md` — Project documentation.
- `docs/deployment/production-checklist.md` — Project documentation.
- `docs/deployment/production-deployment.md` — Project documentation.
- `docs/deployment/systemd-example.md` — Project documentation.
- `docs/operations/configuration.md` — Project documentation.
- `docs/operations/database-bootstrap.md` — Project documentation.
- `docs/operations/migrations-and-troubleshooting.md` — Project documentation.
- `docs/operations/running-project.md` — Project documentation.
- `docs/rag_configuration.md` — Project documentation.
- `docs/roadmap/next-phase-multi-agent.md` — Project documentation.
- `docs/roadmap/phase-4-17-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-18-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-19-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-20-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-20-implementation.md` — Project documentation.
- `docs/roadmap/phase-4-4-5-to-4-11-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-foundation-closeout.md` — Project documentation.
- `docs/roadmap/phase-4-implementation-plan.md` — Project documentation.
- `docs/security/security-baseline.md` — Project documentation.
- `docs/testing/RUNTIME_SCENARIOS.md` — Project documentation.
- `docs/testing/TESTING_STRATEGY.md` — Project documentation.
- `docs/testing/TEST_CATALOG.md` — Project documentation.
- `docs/testing/multi-agent-test-methodology.md` — Project documentation.
- `docs/testing/performance.md` — Project documentation.
- `docs/testing/testing-and-evaluation.md` — Project documentation.
- `docs/ui/investigations.md` — Project documentation.
- `docs/workflows/current-workflows.md` — Project documentation.

## Maintenance rule

Regenerate this document whenever files are added, removed, or substantially repurposed. Descriptions are derived from path conventions, module docstrings, and public classes/functions; core files have explicit descriptions in the generator.
