# Complete Test Catalog

Generated from the current checkout.

Regenerate with:

```powershell
uv run python tools/dev/generate_test_catalog.py
```

## Pytest files

### `tests/test_admin_system_api.py`

- `test_system_runtime_api_exposes_supervisor_and_tools`

### `tests/test_admin_system_web.py`

- `test_system_runtime_page_is_available`

### `tests/test_agent_job_persistence.py`

- `test_agent_job_error_messages_are_bounded_to_schema_contract`

### `tests/test_aggregate_readiness.py`

- `test_aggregate_combines_sources`
- `test_sample_deficits_are_reported`
- `test_one_real_runtime_sample_is_not_ready`
- `test_hard_failure_blocks_when_samples_sufficient`

### `tests/test_architecture_dependencies.py`

- `test_core_has_no_outer_layer_dependencies`
- `test_capabilities_do_not_depend_on_interfaces_composition_or_runtime`
- `test_infrastructure_does_not_depend_on_interface_or_runtime_layers`
- `test_legacy_application_packages_are_absent`
- `test_application_sources_do_not_import_deleted_namespaces`
- `test_application_import_graph_is_acyclic`

### `tests/test_c14_10_claude_observability.py`

- `test_trace_normalizes_runtime_evidence`
- `test_summary_exposes_failures_tools_and_mcp_health`
- `test_completed_job_missing_required_tools_is_visible`
- `test_missing_job_returns_none`

### `tests/test_c14_11_runtime_contract.py`

- `test_c14_11_runtime_allows_mandatory_operational_tools`
- `test_c14_11_native_prompt_requires_real_mcp_execution`

### `tests/test_c14_11a3_ollama_only_contract.py`

- `test_c14_11a3_removes_legacy_runtime_surfaces`
- `test_c14_11a3_runtime_dependencies_are_ollama_only`
- `test_c14_11a3_no_openai_implementation_surfaces_remain`
- `test_c14_11a3_ollama_implementations_remain`

### `tests/test_c14_11a4_1_composition_boundary.py`

- `test_composition_owns_the_application_container`
- `test_composition_builder_owns_dependency_wiring`
- `test_composition_package_exists_as_explicit_boundary`

### `tests/test_c14_11a4_2a_repository_composition.py`

- `test_repository_construction_lives_in_repository_composition_module`
- `test_repository_composition_module_is_not_eager`

### `tests/test_c14_11a4_2b_container_services_composition.py`

- `test_application_container_is_outside_builder`
- `test_core_service_construction_is_outside_builder`
- `test_analysis_and_runtime_are_outside_builder`

### `tests/test_c14_11a4_2c_analysis_investigation_composition.py`

- `test_analysis_and_investigation_composition_is_outside_builder`
- `test_claude_mcp_and_scheduler_wiring_moves_to_runtime_composition`

### `tests/test_c14_11a4_2d_runtime_composition.py`

- `test_runtime_composition_is_outside_builder`
- `test_runtime_composition_keeps_ollama_claude_contract`
- `test_builder_is_composition_coordinator_after_a4_2d`

### `tests/test_c14_11a4_3a_ollama_infrastructure_boundary.py`

- `test_ollama_provider_implementations_live_in_infrastructure`
- `test_analysis_capability_factories_use_infrastructure_implementations`
- `test_legacy_ollama_modules_are_removed`

### `tests/test_c14_11a4_3b_investigation_ollama_infrastructure.py`

- `test_investigation_ollama_adapters_live_in_infrastructure`
- `test_investigation_capability_keeps_contracts_not_ollama_implementations`
- `test_capability_contracts_resolve_provider_adapters_lazily`

### `tests/test_c14_11a4_3c_database_infrastructure_boundary.py`

- `test_database_core_implementation_lives_in_infrastructure`
- `test_repository_implementations_live_only_in_infrastructure`
- `test_production_composition_uses_infrastructure_repositories`
- `test_shared_database_package_is_removed_after_boundary_closure`

### `tests/test_c14_11a4_3d_database_models_migrations_boundary.py`

- `test_database_models_live_only_in_infrastructure`
- `test_production_uses_infrastructure_model_imports`
- `test_engine_registers_infrastructure_models`
- `test_migrations_have_one_canonical_owner`

### `tests/test_c14_12_runtime_readiness.py`

- `test_c14_12_startup_recovers_interrupted_jobs`
- `test_c14_12_mcp_surface_is_bounded_and_stable`
- `test_c14_12_unknown_and_unregistered_tools_fail_closed`
- `test_c14_12_claude_malformed_output_fails_closed`
- `test_c14_12_controlled_policy_and_provider_failures_are_measured`

### `tests/test_c14_7_smoke_schema_init.py`

- `test_c14_7_smoke_initializes_schema_before_container`
- `test_c14_7_smoke_preserves_direct_project_import_fix`

### `tests/test_c14_7_stream_runtime_evidence.py`

- `test_stream_json_operational_success_is_evidence_based`
- `test_operational_success_rejects_failed_mcp`
- `test_operational_success_rejects_missing_required_tool`
- `test_result_error_subtype_is_not_accepted`

### `tests/test_c14_8_project_boundary_decomposition.py`

- `test_c14_8_public_tool_contract_is_unchanged`
- `test_c14_8_project_boundary_is_thin_public_facade`
- `test_c14_8_bounded_modules_own_tool_implementations`
- `test_c14_8_mcp_package_export_is_lazy_and_cycle_free`

### `tests/test_c14_9_claude_native_orchestration.py`

- `test_c14_9_legacy_python_orchestrators_are_removed`
- `test_c14_9_monitoring_service_is_execution_only`
- `test_c14_9_runtime_exports_only_native_claude_orchestration`
- `test_c14_9_domain_packages_drop_old_orchestration_exports`
- `test_c14_9_supervisor_fails_closed_when_runtime_disabled`
- `test_c14_9_composition_has_no_python_orchestration_fallback`
- `test_c14_9_main_has_no_analysis_worker_lifecycle`

### `tests/test_claude_agent_job_persistence.py`

- `test_job_is_created_from_runtime_request`
- `test_job_completion_preserves_result_observability`
- `test_job_survives_repository_recreation`
- `test_interrupted_jobs_are_recovered_as_failed`
- `test_recent_jobs_can_be_filtered_by_status`

### `tests/test_claude_bounded_agents.py`

- `test_canonical_agent_set_is_two_bounded_roles`
- `test_server_supervisor_is_main_session_coordinator`
- `test_specialist_worker_cannot_delegate_or_remediate`
- `test_server_supervisor_has_no_raw_execution_tools`
- `test_specialist_worker_has_no_raw_execution_tools`
- `test_investigation_skill_delegates_only_specialist_worker`
- `test_legacy_agent_files_are_removed`

### `tests/test_claude_code_runtime_configuration.py`

- `test_project_mcp_server_is_registered_for_claude_code`
- `test_claude_settings_use_enforced_permissions`
- `test_claude_agents_have_frontmatter_and_tools`
- `test_server_supervisor_can_delegate_only_specialist_worker`
- `test_specialist_worker_cannot_spawn_agents`
- `test_commands_are_not_a_second_workflow_surface`
- `test_global_rules_are_invariants_only`
- `test_placeholder_hooks_are_not_checked_in`
- `test_active_runtime_instructions_do_not_claim_c1_structure_only`

### `tests/test_claude_least_privilege.py`

- `test_settings_allow_only_current_runtime_capabilities`
- `test_raw_remediation_escape_tools_are_explicitly_denied`
- `test_raw_operational_shell_paths_are_denied_for_both_shells`
- `test_skill_inline_shell_execution_is_disabled`
- `test_runtime_agents_use_inherited_model_and_dontask`
- `test_server_supervisor_uses_supervised_remediation_tools`
- `test_specialist_worker_has_no_remediation_tools`

### `tests/test_claude_operational_skills.py`

- `test_operational_skill_set_is_canonical`
- `test_skills_have_frontmatter_and_exact_intended_tools`
- `test_skills_define_operational_contract_sections`
- `test_analysis_skill_never_forces_normal_analysis`
- `test_investigation_skill_preserves_db_specialist_authority`
- `test_remediation_skill_is_supervised_and_approval_gated`
- `test_server_supervisor_preloads_canonical_workflow_skills`
- `test_specialist_worker_is_not_a_workflow_coordinator`
- `test_legacy_skill_names_are_removed`

### `tests/test_claude_process_session_runner.py`

- `test_process_runner_decodes_structured_output`
- `test_process_runner_accepts_result_text_envelope`
- `test_process_runner_rejects_invalid_json_output`
- `test_process_runner_returns_controlled_nonzero_failure`
- `test_process_runner_requires_project_root_cwd`
- `test_adapter_timeout_terminates_active_process`
- `test_cancel_by_job_id_terminates_process`
- `test_command_environment_is_applied_without_prompt_transport`
- `test_decoder_accepts_strict_batched_event_array`
- `test_decoder_rejects_event_array_without_final_result`
- `test_decoder_rejects_event_array_session_mismatch`
- `test_decoder_surfaces_error_max_turns_result`
- `test_decoder_counts_tool_use_blocks_from_event_array`
- `test_decoder_uses_final_assistant_text_when_success_result_omits_result`
- `test_decoder_rejects_tool_use_message_as_final_text_fallback`
- `test_decoder_success_event_array_can_use_final_assistant_text`
- `test_decoder_does_not_use_tool_message_as_final_fallback`

### `tests/test_claude_project_mcp_runtime_config.py`

- `test_vps_project_mcp_is_explicitly_approved`
- `test_vps_mcp_launch_is_project_root_stable`

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

### `tests/test_claude_runtime_hooks.py`

- `test_settings_register_only_concrete_runtime_hooks`
- `test_hook_handlers_use_cross_platform_exec_form`
- `test_normal_development_session_is_ignored`
- `test_runtime_preflight_passes_current_c14_contract`
- `test_runtime_preflight_blocks_non_ollama_provider`
- `test_session_start_adds_runtime_context_without_blocking`
- `test_runtime_config_change_is_blocked`
- `test_specialist_lifecycle_audit_does_not_store_prompt_or_output`
- `test_runtime_event_directory_is_gitignored`
- `test_runtime_preflight_accepts_hardened_project_mcp_command`
- `test_project_mcp_validation_accepts_hardened_argv`

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

- `test_removed_domain_package_has_no_boundary_to_audit`

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

### `tests/test_ollama_claude_runtime.py`

- `test_direct_claude_uses_ollama_backend`
- `test_runtime_composition_uses_direct_claude_settings`

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
- `test_malformed_evidence_reference_fails_closed`
- `test_foreign_investigation_evidence_fails_closed`
- `test_foreign_server_evidence_fails_closed`
- `test_evidence_without_context_fails_closed`

### `tests/test_phase5_admin_api.py`

- `test_phase5_admin_routes_are_registered`
- `test_phase5_admin_page_is_operator_review_surface`

### `tests/test_phase5_readiness.py`

- `test_phase5_gate_requires_all_metrics_and_real_acceptance`
- `test_phase5_gate_passes_only_with_explicit_real_acceptance`

### `tests/test_phase5_supervised_remediation.py`

- `test_raw_command_and_unknown_write_tool_are_rejected`
- `test_supervised_execution_rechecks_approval_server_and_idempotency`
- `test_rejected_and_expired_approval_cannot_execute`
- `test_execution_and_verification_failures_are_not_reported_as_success`
- `test_rollback_uses_only_registered_reverse_action_and_records_evidence`
- `test_rollback_failure_is_explicit_and_not_hidden`
- `test_state_aware_rollback_requires_original_inactive_state_for_start`
- `test_state_aware_rollback_requires_original_active_state_for_stop`
- `test_restart_and_reload_are_not_declared_reversible`
- `test_foreign_or_mismatched_before_evidence_cannot_authorize_rollback`
- `test_prior_active_state_does_not_make_start_reversible`
- `test_no_solution_found_is_a_persisted_normal_outcome`

### `tests/test_phase6_native_sandbox_runtime.py`

- `test_native_sandbox_runtime_fails_closed_without_attestation`
- `test_native_sandbox_runtime_requires_all_isolation_claims`
- `test_native_sandbox_runtime_accepts_complete_attestation_in_wsl`

### `tests/test_phase6_readiness.py`

- `test_phase6_real_runtime_blocker_keeps_gate_closed`
- `test_phase6_gate_requires_all_thirteen_metrics`

### `tests/test_phase6_sandbox_validation.py`

- `test_validation_contracts_and_invalid_target_fail_closed`
- `test_successful_validation_persists_evidence_and_allows_approval`
- `test_action_or_verification_failure_blocks_approval`
- `test_changed_fingerprint_marks_validation_stale_and_blocks_approval`
- `test_restart_and_reload_cannot_be_validated_without_restoration`
- `test_native_sandbox_runtime_is_required_by_default`

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

- `tools/run_project_mcp_server.py`

## Standard commands

```powershell
uv run python -m pytest
uv run python tools/dev/list_routes.py
uv run python tools/acceptance/run_evaluation_dataset.py
uv run python tools/acceptance/run_safety_runtime_evaluation.py
uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 500
uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500
```

See `TESTING_STRATEGY.md` for when each layer is required.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
