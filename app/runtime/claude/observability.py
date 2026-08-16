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


class ClaudeAgentObservabilityService:
    """
    خدمة تلخص آثار مهام Claude لتوضيح ما شغلته الجلسة وما انتهت إليه.
    """

    REQUIRED_OPERATIONAL_TOOLS = (
        "mcp__vps__run_monitoring",
        "mcp__vps__analyze_report",
    )

    def __init__(
        self,
        repository: AgentJobRepository,
    ) -> None:
        """
        يجهز مصادر قراءة المهام والتقارير اللازمة لبناء أثر تشغيل قابل للمراجعة.
        """
        self._repository = repository

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
        failed = sum(
            statuses.get(status, 0)
            for status in (
                "failed",
                "timed_out",
                "cancelled",
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
            "success_rate": (
                completed / len(traces)
                if traces
                else None
            ),
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

    def _serialize_job(
        self,
        model,
    ) -> dict[str, Any]:
        """
        يحول سجل المهمة إلى بيانات عرض موحدة دون فقدان سبب الفشل أو سياق السيرفر.
        """
        usage = dict(
            getattr(
                model,
                "usage_metadata",
                None,
            )
            or {}
        )
        metadata = dict(
            getattr(
                model,
                "job_metadata",
                None,
            )
            or {}
        )

        tool_calls = self._tool_names(usage)
        mcp_servers = self._mcp_servers(usage)

        duration_ms = self._number(
            usage.get("duration_ms")
        )

        if duration_ms is None:
            duration_ms = self._duration_ms(
                getattr(
                    model,
                    "started_at",
                    None,
                ),
                getattr(
                    model,
                    "completed_at",
                    None,
                ),
            )

        input_tokens = self._number(
            usage.get("input_tokens")
        )
        output_tokens = self._number(
            usage.get("output_tokens")
        )

        model_usage = usage.get("modelUsage")

        if isinstance(model_usage, dict):
            usages = [
                value
                for value in model_usage.values()
                if isinstance(value, dict)
            ]

            if input_tokens is None:
                input_tokens = sum(
                    self._number(
                        item.get("inputTokens")
                    )
                    or 0
                    for item in usages
                )

            if output_tokens is None:
                output_tokens = sum(
                    self._number(
                        item.get("outputTokens")
                    )
                    or 0
                    for item in usages
                )
        else:
            model_usage = {}

        specialist_tools = {
            "Agent(specialist-worker)",
            "mcp__vps__run_specialist",
        }
        specialist_mcp_count = sum(
            1
            for name in tool_calls
            if name == "mcp__vps__run_specialist"
        )
        specialist_agent_count = sum(
            1
            for name in tool_calls
            if name == "Agent(specialist-worker)"
        )
        accepted_specialist_count = usage.get(
            "accepted_specialist_execution_count",
        )
        if not isinstance(accepted_specialist_count, int):
            accepted_specialist_count = specialist_mcp_count

        return {
            "job_id": model.job_id,
            "job_type": model.job_type,
            "server_id": model.server_id,
            "status": model.status,
            "session_id": model.claude_session_id,
            "created_at": self._iso(
                model.created_at
            ),
            "started_at": self._iso(
                model.started_at
            ),
            "completed_at": self._iso(
                model.completed_at
            ),
            "duration_ms": duration_ms,
            "api_duration_ms": self._number(
                usage.get("duration_api_ms")
            ),
            "turn_count": model.turn_count,
            "tool_call_count": model.tool_call_count,
            "tool_calls": tool_calls,
            "unique_tool_calls": list(
                dict.fromkeys(tool_calls)
            ),
            "required_operational_tools": list(
                self.REQUIRED_OPERATIONAL_TOOLS
            ),
            "required_tools_verified": all(
                required in tool_calls
                for required
                in self.REQUIRED_OPERATIONAL_TOOLS
            ),
            "mcp_servers": mcp_servers,
            "mcp_connected": (
                bool(mcp_servers)
                and all(
                    item.get("status")
                    == "connected"
                    for item in mcp_servers
                )
            ),
            # قد تظهر المهمة ونداء الأداة كسجلين لنفس الفحص؛ نعد النداء المقبول
            # مرة واحدة حتى لا نضخم صورة نشاط العامل.
            "specialist_delegation_count": (
                specialist_mcp_count
                if specialist_mcp_count
                else specialist_agent_count
            ),
            "accepted_specialist_execution_count": accepted_specialist_count,
            "completed_specialist_slugs": list(
                usage.get("completed_specialist_slugs", [])
                if isinstance(usage.get("completed_specialist_slugs", []), list)
                else []
            ),
            "investigation_started": (
                "mcp__vps__start_investigation"
                in tool_calls
            ),
            "remediation_proposed": (
                "mcp__vps__propose_remediation"
                in tool_calls
            ),
            "subtype": usage.get("subtype"),
            "stop_reason": usage.get(
                "stop_reason"
            ),
            "is_error": bool(
                usage.get("is_error", False)
            ),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_cost_usd": self._number(
                usage.get("total_cost_usd")
            ),
            "model_usage": model_usage,
            "error_code": model.error_code,
            "error_message": model.error_message,
            "runtime": metadata.get("runtime"),
            "provider": metadata.get("provider"),
            "agent": metadata.get("agent"),
            "max_turns": metadata.get("max_turns"),
            "allowed_tool_count": len(
                metadata.get("allowed_tools", ())
                if isinstance(
                    metadata.get("allowed_tools", ()),
                    (list, tuple),
                )
                else ()
            ),
        }

    @staticmethod
    def _tool_names(
        usage: dict[str, Any],
    ) -> list[str]:
        """
        يستخرج أسماء الأدوات المستخدمة من بيانات المهمة بصيغة مستقرة للعرض والعد.
        """
        raw = usage.get("event_tool_names")

        if not isinstance(raw, list):
            return []

        return [
            item.strip()
            for item in raw
            if isinstance(item, str)
            and item.strip()
        ]

    @staticmethod
    def _mcp_servers(
        usage: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        يلخص خوادم MCP التي ظهرت في أثر الجلسة وحالتها التشغيلية.
        """
        raw = usage.get("event_mcp_servers")

        if not isinstance(raw, list):
            return []

        result = []

        for item in raw:
            if not isinstance(item, dict):
                continue

            result.append(
                {
                    "name": item.get("name"),
                    "status": item.get("status"),
                }
            )

        return result

    @staticmethod
    def _duration_ms(
        started_at: datetime | None,
        completed_at: datetime | None,
    ) -> float | None:
        """
        يحسب مدة المهمة بالميلي ثانية من أوقاتها المحفوظة أو يعيد قيمة فارغة عند غيابها.
        """
        if (
            started_at is None
            or completed_at is None
        ):
            return None

        return (
            completed_at - started_at
        ).total_seconds() * 1000.0

    @staticmethod
    def _number(
        value: Any,
    ) -> int | float | None:
        """
        يقرأ قيمة رقمية من بيانات الأثر مع منع القيم غير الصالحة من إفساد الملخص.
        """
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return value

        return None

    @staticmethod
    def _iso(
        value: datetime | None,
    ) -> str | None:
        """
        يحول وقت المهمة إلى نص زمني موحد للاستخدام في سجل الأثر.
        """
        if value is None:
            return None

        return value.isoformat()
