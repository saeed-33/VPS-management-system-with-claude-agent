"""
قراءة آثار مهام Claude وعرض نشاطها التشغيلي.

تجمع الخدمة حالة المهمة والجلسة والأدوات والمدة والاستخدام في بيانات تساعد على
معرفة ما حدث أثناء المراقبة دون الخلط بين أثر التشغيل وتشخيص السيرفر.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)


class _TraceQueriesMixin:
    """ينظم مجموعة من عمليات المكون."""

    def get_trace(
        self,
        job_id: str,
    ) -> dict[str, Any] | None:
        """
        يسترجع الأثر التفصيلي لمهمة Claude واحدة مع حالتها وجلسة التنفيذ والنتيجة.
        """
        if not job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        model = self._repository.get_by_job_id(
            job_id
        )

        if model is None:
            return None

        return self._serialize_job(model)

    def list_recent_traces(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        يعرض آثار المهام الحديثة بترتيب يساعد على متابعة نشاط المراقبة عبر الزمن.
        """
        if limit < 1 or limit > 500:
            raise ValueError(
                "limit must be between 1 and 500."
            )

        if (
            server_id is not None
            and server_id < 1
        ):
            raise ValueError(
                "server_id must be >= 1."
            )

        normalized_status = (
            status.strip()
            if status is not None
            else None
        )

        if normalized_status == "":
            normalized_status = None

        models = self._repository.list_recent(
            limit=limit,
            server_id=server_id,
            status=normalized_status,
        )

        return [
            self._serialize_job(model)
            for model in models
        ]

    def summarize_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
    ) -> dict[str, Any]:
        """
        يجمع الآثار الحديثة في ملخص يوضح الحالات والمهل والأدوات ومعدل نجاح التشغيل.
        """
        traces = self.list_recent_traces(
            limit=limit,
            server_id=server_id,
        )

        statuses = Counter(
            trace["status"]
            for trace in traces
        )

        completed = statuses.get(
            "completed",
            0,
        )
        active = sum(
            statuses.get(status, 0)
            for status in (
                "queued",
                "running",
            )
        )
        failed = sum(
            statuses.get(status, 0)
            for status in (
                "failed",
                "timed_out",
                "cancelled",
            )
        )
        terminal = completed + failed

        error_code_counts = Counter(
            trace["error_code"]
            for trace in traces
            if trace.get("error_code")
        )
        diagnostic_gap_count = sum(
            1
            for trace in traces
            if (
                trace["status"]
                in {
                    "failed",
                    "timed_out",
                    "cancelled",
                }
                and not str(
                    trace.get("error_message") or ""
                ).strip()
            )
        )

        duration_values = [
            trace["duration_ms"]
            for trace in traces
            if isinstance(
                trace["duration_ms"],
                (int, float),
            )
        ]

        tool_counts = Counter(
            tool_name
            for trace in traces
            for tool_name in trace["tool_calls"]
        )

        return {
            "sample_size": len(traces),
            "server_id": server_id,
            "statuses": dict(
                sorted(statuses.items())
            ),
            "completed_count": completed,
            "failed_count": failed,
            "active_count": active,
            "terminal_count": terminal,
            "success_rate": (
                completed / len(traces)
                if traces
                else None
            ),
            "terminal_success_rate": (
                completed / terminal
                if terminal
                else None
            ),
            "error_code_counts": dict(
                sorted(error_code_counts.items())
            ),
            "diagnostic_gap_count": diagnostic_gap_count,
            "average_duration_ms": (
                sum(duration_values)
                / len(duration_values)
                if duration_values
                else None
            ),
            "average_tool_calls": (
                sum(
                    trace["tool_call_count"]
                    for trace in traces
                )
                / len(traces)
                if traces
                else None
            ),
            "total_tool_calls": sum(
                trace["tool_call_count"]
                for trace in traces
            ),
            "specialist_delegation_count": sum(
                trace["specialist_delegation_count"]
                for trace in traces
            ),
            "mcp_disconnected_job_count": sum(
                1
                for trace in traces
                if trace["mcp_servers"]
                and not trace["mcp_connected"]
            ),
            "required_tool_verification_failure_count": sum(
                1
                for trace in traces
                if (
                    trace["status"] == "completed"
                    and not trace["required_tools_verified"]
                )
            ),
            "top_tools": [
                {
                    "tool_name": tool_name,
                    "count": count,
                }
                for tool_name, count
                in tool_counts.most_common(15)
            ],
        }
