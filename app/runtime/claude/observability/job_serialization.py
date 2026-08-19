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


class _JobSerializationMixin:
    """ينظم مجموعة من عمليات المكون."""

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
