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


def build_read_definitions() -> list[ProjectToolDefinition]:
    integer_id = _integer_id()
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
    ]
