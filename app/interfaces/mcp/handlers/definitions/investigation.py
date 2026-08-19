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


def build_investigation_definitions() -> list[ProjectToolDefinition]:
    integer_id = _integer_id()
    return [
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
    ]
