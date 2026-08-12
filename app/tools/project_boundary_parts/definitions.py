from __future__ import annotations

from app.mcp.schemas import ProjectToolDefinition


class BoundaryDefinitionsMixin:
    @staticmethod
    def _build_definitions() -> list[
        ProjectToolDefinition
    ]:
        integer_id = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        return [
            ProjectToolDefinition(
                tool_id="get_server_context",
                description=(
                    "Read server context through "
                    "project services."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_monitoring_profile",
                description=(
                    "Read monitoring profile and "
                    "assigned commands."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "profile_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["profile_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="run_monitoring",
                description=(
                    "Run existing project-owned "
                    "monitoring for a server."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_report",
                description=(
                    "Read a persisted monitoring "
                    "report."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_latest_report",
                description=(
                    "Read the latest persisted report "
                    "for a server."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="find_exact_report_match",
                description=(
                    "Find a completed analysis with "
                    "the same report fingerprint."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="search_similar_incidents",
                description=(
                    "Search historical incident RAG "
                    "for similar reports."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_top_similar_reports",
                description=(
                    "Return at most the top 3 similar "
                    "historical reports."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="analyze_report",
                description=(
                    "Analyze a report through the "
                    "existing AnalysisOrchestrator."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "force": {
                            "type": "boolean",
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_analysis",
                description=(
                    "Read persisted report analysis by "
                    "analysis_id or report_id."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "analysis_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="search_knowledge",
                description=(
                    "Search project-owned Knowledge RAG."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                        },
                        "specialist_slug": {
                            "type": "string",
                        },
                        "domains": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 6,
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="start_investigation",
                description=(
                    "Persist an investigation routing "
                    "decision for a report and analysis."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "analysis_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "required": ["report_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="get_investigation",
                description=(
                    "Read a persisted investigation "
                    "detail model."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_investigation_status",
                description=(
                    "Read investigation status and "
                    "selected Specialists."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_evidence",
                description=(
                    "Read persisted runtime Evidence "
                    "for an investigation."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_available_specialists",
                description=(
                    "Read enabled Specialist runtime "
                    "definitions from the DB-backed "
                    "registry."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "domains": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        }
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_specialist_definition",
                description=(
                    "Read one enabled Specialist "
                    "runtime definition by slug."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "specialist_slug": {
                            "type": "string",
                        }
                    },
                    "required": ["specialist_slug"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="run_specialist",
                description=(
                    "Run a selected Specialist through "
                    "the existing Ollama-backed "
                    "specialist investigation loop."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        },
                        "specialist_slug": {
                            "type": "string",
                        },
                        "objective": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "investigation_id",
                        "specialist_slug",
                        "objective",
                    ],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="propose_remediation",
                description=(
                    "Create a grounded remediation "
                    "proposal linked to diagnosis "
                    "claims and Evidence."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        },
                        "problem_summary": {
                            "type": "string",
                        },
                        "diagnosis_claim_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                    "required": [
                        "investigation_id",
                        "problem_summary",
                        "diagnosis_claim_ids",
                        "evidence_ids",
                    ],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="create_remediation_plan",
                description=(
                    "Persist an auditable remediation "
                    "plan before sandbox validation."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        },
                        "investigation_id": {
                            "type": "string",
                        },
                        "title": {
                            "type": "string",
                        },
                        "problem_summary": {
                            "type": "string",
                        },
                        "proposed_actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                            },
                        },
                        "diagnosis_claim_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "risk_level": {
                            "type": "string",
                        },
                        "rollback_plan": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "investigation_id",
                        "title",
                        "problem_summary",
                        "proposed_actions",
                        "diagnosis_claim_ids",
                        "evidence_ids",
                    ],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="test_remediation_in_sandbox",
                description=(
                    "Validate a remediation plan in an "
                    "isolated sandbox dry-run."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        }
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="get_sandbox_result",
                description=(
                    "Read an auditable sandbox result "
                    "by result_id or plan_id."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "result_id": {
                            "type": "string",
                        },
                        "plan_id": {
                            "type": "string",
                        },
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="request_user_approval",
                description=(
                    "Record that a remediation plan "
                    "requires explicit user approval."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        }
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="apply_approved_remediation",
                description=(
                    "Attempt production application "
                    "only after sandbox and policy "
                    "authorization."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        },
                        "approved_by": {
                            "type": "string",
                        },
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
        ]
