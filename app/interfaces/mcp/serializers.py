"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from collections.abc import Mapping
from typing import Any


def serialize_value(
    value: Any,
) -> Any:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_value؛ المدخلات المهمة: value.
    تعيد Any أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_server؛ المدخلات المهمة: server.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_profile؛ المدخلات المهمة: profile، commands.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_monitoring_report_data؛ المدخلات المهمة: report.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        report
    )


def serialize_report_details(
    report,
) -> dict[str, Any]:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_report_details؛ المدخلات المهمة: report.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        report
    )


def serialize_analysis(
    analysis,
) -> dict[str, Any]:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_analysis؛ المدخلات المهمة: analysis.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_incident_context؛ المدخلات المهمة: context.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        context
    )


def serialize_knowledge_context(
    context,
) -> dict[str, Any]:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_knowledge_context؛ المدخلات المهمة: context.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        context
    )


def serialize_specialist_definition(
    specialist,
) -> dict[str, Any]:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_specialist_definition؛ المدخلات المهمة: specialist.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        specialist
    )


def serialize_specialist_loop_result(
    result,
) -> dict[str, Any]:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى serialize_specialist_loop_result؛ المدخلات المهمة: result.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return serialize_value(
        result
    )
