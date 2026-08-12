# Complete Test Catalog

Generated from the current checkout.

Regenerate with:

```powershell
uv run python tools/generate_test_catalog.py
```

## Pytest files

### `tests/test_admin_system_api.py`

- `test_system_runtime_api_exposes_supervisor_and_tools`

### `tests/test_admin_system_web.py`

- `test_system_runtime_page_is_available`

### `tests/test_aggregate_readiness.py`

- `test_aggregate_combines_sources`
- `test_sample_deficits_are_reported`
- `test_one_real_runtime_sample_is_not_ready`
- `test_hard_failure_blocks_when_samples_sufficient`

### `tests/test_claude_agent_job_persistence.py`

- `test_job_is_created_from_runtime_request`
- `test_job_completion_preserves_result_observability`
- `test_job_survives_repository_recreation`
- `test_interrupted_jobs_are_recovered_as_failed`
- `test_recent_jobs_can_be_filtered_by_status`

### `tests/test_claude_code_runtime_configuration.py`

- `test_project_mcp_server_is_registered_for_claude_code`
- `test_claude_settings_use_enforced_permissions`
- `test_claude_agents_have_frontmatter_and_tools`
- `test_monitoring_supervisor_can_delegate_to_agent`

### `tests/test_claude_multi_specialist_supervision.py`

- `test_multi_specialist_supervision_runs_selected_specialists_sequentially`
- `test_multi_specialist_supervision_respects_max_specialists`
- `test_multi_specialist_supervision_fails_when_tool_budget_is_exceeded`
- `test_multi_specialist_supervision_stops_on_tool_failure`
- `test_multi_specialist_supervision_completes_when_none_selected`

### `tests/test_claude_runtime_adapter.py`

- `test_bounded_claude_invocation_succeeds`
- `test_timeout_is_returned_as_controlled_result`
- `test_runtime_failure_is_returned_as_controlled_result`
- `test_invalid_structured_output_is_rejected`
- `test_operational_tool_access_is_disabled_in_c2`
- `test_claude_reported_failure_remains_failed`

### `tests/test_claude_runtime_documentation.py`

- `test_project_structure_documents_runtime_files`
- `test_runtime_operations_doc_matches_configured_ollama_defaults`
- `test_runtime_documentation_has_current_verification_commands`
- `test_r5_status_and_test_catalog_are_documented`

### `tests/test_claude_supervised_monitoring_cycle.py`

- `test_cycle_executes_fixed_tool_sequence`
- `test_cycle_persists_successful_job_observability`
- `test_cycle_stops_and_persists_failure_when_tool_fails`
- `test_cycle_fails_when_server_has_no_profile`
- `test_cycle_rejects_invalid_server_id`

### `tests/test_claude_supervisor.py`

- `test_supervisor_delegates_monitoring_cycle`
- `test_supervisor_reports_runtime_status`

### `tests/test_cross_specialist_conflicts.py`

- `test_explicit_conflicting_states_become_unknown`
- `test_matching_explicit_states_do_not_conflict`
- `test_no_state_metadata_keeps_original_certainty_rules`

### `tests/test_cross_specialist_correlation.py`

- `test_live_evidence_high_confidence_is_confirmed`
- `test_live_evidence_lower_confidence_is_probable`
- `test_knowledge_only_finding_remains_unknown`
- `test_same_title_merges_specialists`
- `test_unknown_evidence_reference_fails_closed`

### `tests/test_diagnostic_policy.py`

- `test_policy_allows_registered_assigned_safe_tool`
- `test_policy_denies_unknown_tool`
- `test_policy_denies_unassigned_tool`
- `test_policy_denies_invalid_arguments`
- `test_policy_enforces_specialist_round_limit`
- `test_policy_enforces_investigation_round_limit`
- `test_policy_enforces_specialist_action_limit`
- `test_policy_enforces_investigation_action_limit`
- `test_policy_can_report_multiple_budget_denials`
- `test_policy_request_rejects_invalid_counters`
- `test_denied_result_never_exposes_execution_envelope`

### `tests/test_diagnostic_tool_registry.py`

- `test_default_registry_contains_expected_read_only_tools`
- `test_service_parameter_rejects_shell_injection`
- `test_path_parameter_rejects_shell_injection`
- `test_connect_probe_validates_port`
- `test_safe_command_rendering`
- `test_unknown_arguments_are_rejected`
- `test_specialist_allowlist_blocks_unassigned_tool`
- `test_specialist_allowlist_allows_assigned_tool`
- `test_all_default_tools_are_read_only`

### `tests/test_diagnostic_tools_api.py`

- `test_diagnostic_tools_api_lists_registry`

### `tests/test_domain_boundaries.py`

- `test_domain_does_not_import_runtime_or_mcp_boundaries`

### `tests/test_evaluation_dataset_runner.py`

- `test_default_dataset_meets_gate_sample_counts`
- `test_case_ids_are_unique`
- `test_expected_behavior_executor_wires_gate`
- `test_runtime_failure_blocks_hard_metric`
- `test_executor_must_return_matching_case_id`
- `test_duplicate_case_ids_rejected`

### `tests/test_evidence_collection.py`

- `test_denied_policy_never_touches_repository_or_runner`
- `test_success_becomes_command_result_evidence`
- `test_nonzero_command_is_still_evidence`
- `test_output_is_truncated_to_policy_limit`
- `test_server_specific_key_overrides_default`
- `test_default_key_is_used_when_server_has_none`
- `test_missing_server_does_not_call_runner`
- `test_connection_failure_becomes_evidence`
- `test_empty_output_is_explicit`

### `tests/test_final_diagnosis_synthesizer.py`

- `test_valid_llm_narrative_is_used`
- `test_unknown_claim_id_uses_fallback`
- `test_conflict_must_be_preserved`
- `test_client_failure_uses_deterministic_summary`
- `test_no_client_uses_fallback`
- `test_prompt_contains_only_validated_envelope`

### `tests/test_hybrid_retriever.py`

- `test_weak_vector_candidate_is_rejected_even_with_full_text`
- `test_full_text_only_candidate_never_bypasses_vector_threshold`
- `test_hybrid_candidate_preserves_real_vector_similarity`
- `test_structural_conflict_rejects_high_similarity_candidate`
- `test_compatible_candidate_is_accepted`
- `test_duplicate_vector_and_text_candidate_becomes_one_context`

### `tests/test_investigation_contracts.py`

- `test_default_investigation_state`
- `test_confidence_must_be_normalized`
- `test_duplicate_evidence_is_rejected`
- `test_task_must_belong_to_same_investigation`
- `test_specialist_budget_counts_unique_specialists`
- `test_round_budget_is_enforced`
- `test_result_must_reference_existing_task`
- `test_result_specialist_must_match_task`
- `test_pending_result_is_invalid`
- `test_valid_result_can_be_added`

### `tests/test_investigation_persistence_service.py`

- `test_persistence_preserves_candidate_and_selected_ranks`
- `test_healthy_decision_can_be_persisted_for_audit`

### `tests/test_investigation_read_service.py`

- `test_read_model_does_not_invent_runtime`
- `test_runtime_snapshot_is_exposed_when_persisted`
- `test_summary_exposes_selected_specialists`
- `test_list_limit_is_bounded`

### `tests/test_investigation_router.py`

- `test_healthy_report_has_no_candidates_or_selection`
- `test_cpu_issue_has_same_candidate_and_selection`
- `test_connection_failure_routes_network_only`
- `test_candidate_shortlist_can_exceed_selection_budget`
- `test_candidate_limit_is_independent_from_selection_limit`
- `test_candidate_limit_must_be_at_least_selection_limit`
- `test_memory_issue_selects_memory_specialist`
- `test_combined_cpu_memory_selects_both`
- `test_domain_only_fallback_works_when_no_trigger_matches`
- `test_no_suitable_specialist_is_explicit`
- `test_info_only_issue_is_not_actionable`

### `tests/test_investigation_runtime_snapshot_service.py`

- `test_build_snapshot_serializes_runtime`
- `test_persist_preserves_existing_metadata`
- `test_narrative_is_persisted`
- `test_missing_investigation_fails`

### `tests/test_investigations_api.py`

- `test_list_investigations`
- `test_get_investigation_includes_runtime`
- `test_get_missing_investigation_returns_404`
- `test_list_report_investigations`
- `test_list_limit_validation`

### `tests/test_investigations_web.py`

- `test_investigations_page_is_available`
- `test_investigation_detail_page_is_available`

### `tests/test_knowledge_chunker.py`

- `test_markdown_heading_is_preserved_as_section`
- `test_html_heading_metadata_is_used`
- `test_pdf_page_metadata_preserves_page_number`
- `test_large_document_is_split_under_max_chars`
- `test_chunk_indexes_are_contiguous`

### `tests/test_knowledge_chunking_service.py`

- `test_chunking_service_persists_chunks`

### `tests/test_knowledge_hybrid_retrieval.py`

- `test_hybrid_retrieval_fuses_both_branches`
- `test_specialist_scope_boosts_direct_source`
- `test_vector_only_candidate_is_allowed`

### `tests/test_knowledge_indexer.py`

- `test_indexer_embeds_all_chunks_and_marks_document`
- `test_indexer_skips_current_embedding`
- `test_force_reindexes_current_embedding`

### `tests/test_knowledge_ingestion_contracts.py`

- `test_document_status_lifecycle_is_explicit`
- `test_parsed_document_requires_text`
- `test_parsed_document_accepts_large_document_metadata`
- `test_chunk_draft_preserves_page_and_section`
- `test_chunk_index_is_zero_based`

### `tests/test_knowledge_ingestion_service.py`

- `test_ingestion_persists_parsed_document`

### `tests/test_knowledge_parsers.py`

- `test_normalize_text_collapses_spacing`
- `test_html_parser_removes_script_and_extracts_title`
- `test_plain_text_parser`

### `tests/test_knowledge_retrieval_scope.py`

- `test_scope_condition_contains_specialist`
- `test_scope_condition_accepts_domains`
- `test_empty_scope_is_true`

### `tests/test_knowledge_source_foundation.py`

- `test_url_source_requires_uri`
- `test_inline_source_requires_content`
- `test_create_dto_normalizes_scope`
- `test_registry_excludes_disabled_sources`
- `test_registry_finds_sources_by_domain`
- `test_registry_finds_sources_for_specialist`

### `tests/test_knowledge_source_loader.py`

- `test_inline_loader`
- `test_loader_rejects_unknown_source_type`

### `tests/test_knowledge_source_seed.py`

- `test_seed_slugs_are_unique`
- `test_seed_sources_are_official_https_urls`
- `test_seed_covers_all_baseline_specialists`
- `test_each_seed_has_routing_scope`

### `tests/test_ollama_context_window.py`

- `test_normal_reasoning_uses_32k_context_and_6144_output`
- `test_final_synthesis_uses_32k_context_and_6144_output`

### `tests/test_ollama_final_synthesis_dto.py`

- `test_final_synthesis_minimal_contract_succeeds`

### `tests/test_ollama_final_synthesis_minimal_contract.py`

- `test_final_synthesis_uses_minimal_json_mode`
- `test_normal_reasoning_keeps_existing_generation_limits`

### `tests/test_ollama_specialist_reasoning_client.py`

- `test_schema_rejection_is_cached_and_json_fallback_succeeds`
- `test_length_retry_uses_compact_retry_instruction`
- `test_final_synthesis_enables_provider_compact_mode`

### `tests/test_persisted_runtime_evaluation.py`

- `test_valid_snapshot_emits_five_real_metrics`
- `test_unknown_evidence_fails_grounding`
- `test_budget_overrun_fails`
- `test_unknown_narrative_claim_fails`

### `tests/test_production_readiness_gate.py`

- `test_gate_requires_minimum_samples`
- `test_all_thresholds_pass_supervised_only`
- `test_hard_safety_failure_blocks`
- `test_policy_failure_blocks`
- `test_soft_metric_can_fail_rate_threshold`
- `test_duplicate_thresholds_rejected`

### `tests/test_project_mcp_analysis_tools.py`

- `test_find_exact_report_match_returns_reusable_analysis`
- `test_get_top_similar_reports_is_capped_at_three`
- `test_analyze_report_uses_existing_orchestrator`
- `test_get_analysis_by_report_id`
- `test_search_knowledge_uses_project_retriever`
- `test_missing_dependency_is_controlled_error`

### `tests/test_project_mcp_investigation_tools.py`

- `test_start_investigation_routes_and_persists_decision`
- `test_start_investigation_requires_analysis`
- `test_get_investigation_reads_detail`
- `test_get_investigation_status_returns_compact_state`
- `test_get_evidence_reads_runtime_evidence`
- `test_missing_investigation_is_controlled_error`

### `tests/test_project_mcp_protocol_server.py`

- `test_mcp_initialize_exposes_tool_capability`
- `test_mcp_tools_list_uses_project_tool_definitions`
- `test_mcp_tools_call_returns_structured_project_result`
- `test_mcp_unknown_method_returns_jsonrpc_error`

### `tests/test_project_mcp_remediation_tools.py`

- `test_propose_remediation_requires_diagnosis_and_evidence_links`
- `test_create_plan_and_sandbox_result_are_persisted`
- `test_failed_sandbox_blocks_production_application`
- `test_high_risk_action_requests_user_approval`
- `test_policy_denied_action_cannot_be_applied_even_after_sandbox`

### `tests/test_project_mcp_specialist_tools.py`

- `test_get_available_specialists_reads_enabled_runtime_registry`
- `test_get_specialist_definition_reads_latest_registry_snapshot`
- `test_run_specialist_uses_selected_db_definition_and_budget`
- `test_run_specialist_rejects_unselected_specialist`
- `test_run_specialist_requires_configured_loop`

### `tests/test_project_mcp_tool_boundary.py`

- `test_tool_inventory_is_deliberately_small`
- `test_get_server_context_uses_project_service`
- `test_get_monitoring_profile_includes_commands`
- `test_run_monitoring_invokes_existing_service_and_reads_report`
- `test_get_report_reads_persisted_report`
- `test_get_latest_report_returns_controlled_not_found`
- `test_invalid_input_is_normalized`
- `test_unknown_tool_is_rejected`

### `tests/test_project_tool_catalog.py`

- `test_every_project_tool_belongs_to_one_group`
- `test_boundary_exposes_grouped_tool_definitions`
- `test_tool_group_lookup_rejects_unknown_tools`

### `tests/test_rag_evaluation_contract.py`

- `test_hybrid_does_not_use_rrf_as_vector_similarity`
- `test_orchestrator_persists_vector_similarity_not_rrf`
- `test_vector_repository_filters_before_limit`

### `tests/test_reuse_policy.py`

- `test_exact_fingerprint_reuses_analysis`
- `test_force_always_requires_full_analysis`
- `test_compatible_historical_context_is_assisted`
- `test_context_is_ignored_when_assisted_is_disabled`
- `test_no_context_requires_full_analysis`

### `tests/test_route_inventory.py`

- `test_route_inventory_contains_application_routes`
- `test_web_routes_are_excluded_from_openapi`
- `test_specialists_api_is_in_openapi_inventory`
- `test_health_route_remains_visible`

### `tests/test_runtime_readiness_gate.py`

- `test_runtime_readiness_gate_passes_full_non_regressing_matrix`
- `test_runtime_readiness_gate_blocks_missing_runtime_case`
- `test_runtime_readiness_gate_blocks_critical_regression`
- `test_runtime_readiness_gate_blocks_critical_score_regression`
- `test_non_critical_regression_is_recorded_but_does_not_block`
- `test_duplicate_observations_are_rejected`

### `tests/test_safety_runtime_evaluation.py`

- `test_routing_runtime_emits_ten_passes`
- `test_policy_runtime_emits_ten_passes`
- `test_provider_runtime_emits_ten_safe_results`

### `tests/test_server_coordinator.py`

- `test_cpu_and_memory_results_are_collected`
- `test_partial_specialist_failure_preserves_success`
- `test_no_selected_specialists_completes_without_loop`

### `tests/test_server_coordinator_initial_evidence.py`

- `test_initial_connection_failure_becomes_citable_analysis_evidence`
- `test_empty_initial_analysis_produces_no_evidence`

### `tests/test_specialist_context.py`

- `test_context_preserves_knowledge_source_ids`
- `test_irrelevant_evidence_is_excluded`
- `test_knowledge_budget_limits_large_results`
- `test_context_includes_incident_provenance`

### `tests/test_specialist_definition_repository.py`

- `test_create_and_reload`
- `test_slug_is_normalized`
- `test_duplicate_slug_is_rejected`
- `test_invalid_slug_is_rejected`
- `test_update_specialist`
- `test_enabled_filter`
- `test_priority_order`
- `test_delete`

### `tests/test_specialist_investigation_loop.py`

- `test_loop_collects_evidence_then_reasons_again`
- `test_denied_request_forces_synthesis_without_execution`
- `test_last_round_requests_are_not_executed`
- `test_action_budget_stops_additional_execution`
- `test_duplicate_request_is_not_executed_twice`

### `tests/test_specialist_reasoning_agent.py`

- `test_reasoning_converts_valid_output_to_contract`
- `test_unknown_knowledge_citation_is_rejected`
- `test_unknown_recommended_specialist_is_dropped`
- `test_systemd_alias_maps_to_systemd_service`
- `test_prompt_has_no_tool_execution_request`

### `tests/test_specialist_reasoning_client_ollama_compat.py`

- `test_schema_http_400_falls_back_to_json_mode`
- `test_bad_json_retries_once_in_json_mode`
- `test_valid_schema_output_needs_one_request`

### `tests/test_specialist_reasoning_client_structured_output.py`

- `test_ollama_uses_json_schema_as_format`
- `test_ollama_retries_once_after_invalid_json`
- `test_ollama_valid_output_does_not_retry`

### `tests/test_specialist_reasoning_objective_prompt.py`

- `test_objective_is_prominent_before_and_after_catalog`

### `tests/test_specialist_reasoning_provenance_ids.py`

- `test_evidence_namespace_prefix_is_normalized_only_for_real_id`
- `test_unknown_prefixed_reference_remains_rejected`

### `tests/test_specialist_reasoning_tool_requests.py`

- `test_reasoning_returns_structured_tool_requests`

### `tests/test_specialist_registry.py`

- `test_disabled_specialists_are_excluded`
- `test_snapshot_is_stable_and_uses_one_repository_read`
- `test_registry_order_is_deterministic`
- `test_domain_lookup_is_case_insensitive`
- `test_multi_domain_lookup_prefers_more_matches`
- `test_require_all_filters_partial_matches`
- `test_invalid_definition_fails_snapshot`
- `test_invalid_domains_payload_fails_snapshot`
- `test_duplicate_domains_are_normalized`

### `tests/test_specialists_api.py`

- `test_list_specialists`
- `test_create_specialist`
- `test_duplicate_specialist_returns_409`
- `test_update_and_enable`
- `test_missing_specialist_returns_404`
- `test_delete_specialist`

### `tests/test_structured_compatibility.py`

- `test_identical_structured_state_is_compatible`
- `test_connection_state_conflict_is_rejected`
- `test_command_success_conflict_is_rejected`
- `test_exit_status_class_conflict_is_rejected`
- `test_disjoint_error_signatures_are_rejected`
- `test_invalid_normalized_report_is_rejected`

## Runtime / acceptance tools

- `tools/list_routes.py`
- `tools/run_all_tests.py`
- `tools/run_evaluation_dataset.py`
- `tools/run_investigation_web_api_acceptance.py`
- `tools/run_persisted_runtime_evaluation.py`
- `tools/run_production_readiness_evaluation.py`
- `tools/run_project_mcp_server.py`
- `tools/run_safety_runtime_evaluation.py`
- `tools/run_server_coordinator_acceptance.py`
- `tools/run_specialist_investigation.py`

## Standard commands

```powershell
uv run python -m pytest
uv run python tools/list_routes.py
uv run python tools/run_evaluation_dataset.py
uv run python tools/run_safety_runtime_evaluation.py
uv run python tools/run_persisted_runtime_evaluation.py --limit 500
uv run python tools/run_production_readiness_evaluation.py --limit 500
```

See `TESTING_STRATEGY.md` for when each layer is required.

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


## C.14.2 Operational Skills

- `tests/test_claude_operational_skills.py` validates the canonical Skill set, frontmatter, intended MCP tool grants, operational contract sections, DB-defined Specialist boundary, legacy Skill removal, and proposal-only remediation boundary.


## C.14.3 Bounded Agents

- `tests/test_claude_bounded_agents.py` validates the two-agent architecture, main-session-only specialist delegation, model inheritance, DB Specialist authority, absence of nested delegation, no raw execution tools, and the investigation Skill integration.


## C.14.4 Least Privilege

- `tests/test_claude_least_privilege.py` validates the exact pre-approved runtime tool set, `dontAsk` agent mode, PowerShell/Bash operational denials, disabled Skill shell execution, and explicit Phase 5 remediation denials.

## C.14.5 Concrete Runtime Hooks

- `tests/test_claude_runtime_hooks.py` validates hook registration, portable
  exec-form commands, runtime-only preflight behavior, Ollama/provider gating,
  immutable runtime configuration, Specialist lifecycle event sanitization,
  and the ignored transient runtime-event directory.

## C.14.6 Concrete ClaudeSessionRunner

- `tests/test_claude_process_session_runner.py` validates the subprocess runner
  against local child processes: Claude JSON-envelope decoding, structured
  output forwarding, project-root enforcement, controlled non-zero failures,
  environment injection, explicit cancellation, and timeout process cleanup.
  It does not require Ollama or Claude Code to be installed.

## C.14.7 Ollama-backed Claude Runtime

- `tests/test_ollama_claude_runtime.py` validates launcher argv, model/agent
  inheritance path, strict project MCP configuration, structured output,
  runtime hook markers, persisted job lifecycle, failure propagation, and the
  feature-flagged bootstrap switch.
- `tools/smoke_ollama_claude_runtime.py --server-id <id>` is the required real
  integration smoke and requires `CLAUDE_RUNTIME_ENABLED=true`.
