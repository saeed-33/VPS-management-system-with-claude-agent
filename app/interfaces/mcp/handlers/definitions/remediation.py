"""مجموعات تعريفات أدوات MCP."""
from __future__ import annotations

from app.interfaces.mcp.schemas.definition import ProjectToolDefinition


def _integer_id() -> dict:
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }


def build_remediation_definitions() -> list[ProjectToolDefinition]:
    integer_id = _integer_id()
    return [
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
                    "server_id": {
                        "type": "integer",
                        "minimum": 1,
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
                    "error_classification": {
                        "type": "string",
                        "enum": [
                            "normal",
                            "dangerous",
                            "sensitive",
                        ],
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
                "Validate a remediation plan in the Phase 6 "
                "isolated sandbox when an explicit safe target is "
                "provided; otherwise preserve the Phase 5 dry-run "
                "contract."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                    },
                    "target_server_id": {
                        "type": "integer",
                        "minimum": 1,
                    },
                    "target_server_name": {
                        "type": "string",
                    },
                    "target_service": {
                        "type": "string",
                    },
                },
                "required": ["plan_id"],
                "additionalProperties": False,
            },
            read_only=False,
        ),

        ProjectToolDefinition(
            tool_id="get_sandbox_result",
            description=(
                "Read an auditable Phase 5 sandbox result or Phase 6 "
                "sandbox validation by result_id, validation_id, or "
                "plan_id."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "result_id": {
                        "type": "string",
                    },
                    "validation_id": {
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
                    },
                    "expires_in_seconds": {
                        "type": "integer",
                        "minimum": 60,
                        "maximum": 86400,
                    },
                    "scope": {
                        "type": "object",
                    },
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
                    "approval_id": {
                        "type": "string",
                    },
                    "server_id": {
                        "type": "integer",
                        "minimum": 1,
                    },
                    "actor": {
                        "type": "string",
                    },
                    "idempotency_key": {
                        "type": "string",
                    },
                    "runtime_session_id": {
                        "type": "string",
                    },
                    "agent_job_id": {
                        "type": "string",
                    },
                },
                "required": ["plan_id"],
                "additionalProperties": False,
            },
            read_only=False,
        ),

        ProjectToolDefinition(
            tool_id="attempt_autonomous_remediation",
            description=(
                "Evaluate and, only when the persisted Python policy "
                "gates pass, attempt the bounded start_service action."
            ),
            input_schema={
                "type": "object",
                "properties": {"plan_id": {"type": "string"}},
                "required": ["plan_id"],
                "additionalProperties": False,
            },
            read_only=False,
        ),
    ]
