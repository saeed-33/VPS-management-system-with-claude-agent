from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from collections.abc import Mapping
from typing import Any


def serialize_value(
    value: Any,
) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if is_dataclass(value):
        return {
            field.name: serialize_value(getattr(value, field.name))
            for field in fields(value)
        }

    if hasattr(value, "__mapper__"):
        return {
            column.key: serialize_value(
                getattr(value, column.key)
            )
            for column in value.__mapper__.columns
        }

    if isinstance(value, list | tuple):
        return [
            serialize_value(item)
            for item in value
        ]

    if isinstance(value, Mapping):
        return {
            str(key): serialize_value(item)
            for key, item in value.items()
        }

    return value


def serialize_server(
    server,
) -> dict[str, Any]:
    return {
        "id": server.id,
        "name": server.name,
        "host": server.host,
        "port": server.port,
        "username": server.username,
        "description": server.description,
        "monitor_enabled": server.monitor_enabled,
        "interval_seconds": server.interval_seconds,
        "monitoring_profile_id": (
            server.monitoring_profile_id
        ),
        "status": server.status,
        "last_checked_at": serialize_value(
            server.last_checked_at
        ),
        "last_success_at": serialize_value(
            server.last_success_at
        ),
        "last_error": server.last_error,
        "last_report_id": server.last_report_id,
    }


def serialize_profile(
    profile,
    *,
    commands=None,
) -> dict[str, Any]:
    data = {
        "id": profile.id,
        "name": profile.name,
        "description": profile.description,
        "enabled": profile.enabled,
    }

    if commands is not None:
        data["commands"] = [
            {
                "id": command.id,
                "name": command.name,
                "command": command.command,
                "timeout_seconds": (
                    assignment.custom_timeout_seconds
                    if (
                        assignment.custom_timeout_seconds
                        is not None
                    )
                    else command.timeout_seconds
                ),
                "execution_order": (
                    assignment.execution_order
                ),
                "enabled": assignment.enabled,
            }
            for command, assignment in commands
        ]

    return data


def serialize_monitoring_report_data(
    report,
) -> dict[str, Any]:
    return serialize_value(
        report
    )


def serialize_report_details(
    report,
) -> dict[str, Any]:
    return serialize_value(
        report
    )


def serialize_analysis(
    analysis,
) -> dict[str, Any]:
    return {
        "id": analysis.id,
        "report_id": analysis.report_id,
        "server_id": analysis.server_id,
        "provider_name": analysis.provider_name,
        "model_name": analysis.model_name,
        "status": analysis.status,
        "health_status": analysis.health_status,
        "summary": analysis.summary,
        "issues": serialize_value(
            analysis.issues or []
        ),
        "positive_findings": serialize_value(
            analysis.positive_findings or []
        ),
        "recommended_actions": serialize_value(
            analysis.recommended_actions or []
        ),
        "analysis_source": getattr(
            analysis,
            "analysis_source",
            None,
        ),
        "reused_from_analysis_id": getattr(
            analysis,
            "reused_from_analysis_id",
            None,
        ),
        "retrieval_strategy": getattr(
            analysis,
            "retrieval_strategy",
            None,
        ),
        "retrieval_score": getattr(
            analysis,
            "retrieval_score",
            None,
        ),
        "llm_called": getattr(
            analysis,
            "llm_called",
            None,
        ),
    }


def serialize_incident_context(
    context,
) -> dict[str, Any]:
    return serialize_value(
        context
    )


def serialize_knowledge_context(
    context,
) -> dict[str, Any]:
    return serialize_value(
        context
    )


def serialize_specialist_definition(
    specialist,
) -> dict[str, Any]:
    return serialize_value(
        specialist
    )


def serialize_specialist_loop_result(
    result,
) -> dict[str, Any]:
    return serialize_value(
        result
    )
