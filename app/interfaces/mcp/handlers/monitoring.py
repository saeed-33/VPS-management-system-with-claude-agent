"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: app.interfaces.mcp.schemas، app.interfaces.mcp.serializers.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from typing import Any

from app.interfaces.mcp.schemas import ProjectToolResult
from app.interfaces.mcp.serializers import (
    serialize_monitoring_report_data,
    serialize_profile,
    serialize_report_details,
    serialize_server,
)


class MonitoringToolsMixin:
    """
    يمثل MonitoringToolsMixin مسؤولية محددة داخل طبقة MCP capability boundary.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Claude أو خادم MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def _get_server_context(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_server_context؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        server = self._server_service.get_server(
            server_id
        )

        return ProjectToolResult(
            tool_id="get_server_context",
            success=True,
            data={
                "server": serialize_server(
                    server
                )
            },
        )

    async def _get_monitoring_profile(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_monitoring_profile؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        profile_id = self._required_int(
            arguments,
            "profile_id",
        )

        profile = (
            self._monitoring_profile_service
            .get_profile(
                profile_id
            )
        )
        commands = (
            self._monitoring_profile_service
            .list_profile_commands(
                profile_id
            )
        )

        return ProjectToolResult(
            tool_id="get_monitoring_profile",
            success=True,
            data={
                "profile": serialize_profile(
                    profile,
                    commands=commands,
                )
            },
        )

    async def _run_monitoring(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _run_monitoring؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        report = await self._monitoring_service.run(
            server_id
        )

        latest = self._latest_report_for_server(
            server_id
        )

        return ProjectToolResult(
            tool_id="run_monitoring",
            success=True,
            data={
                "monitoring_report": (
                    serialize_monitoring_report_data(
                        report
                    )
                ),
                "persisted_report": (
                    serialize_report_details(
                        latest
                    )
                    if latest is not None
                    else None
                ),
            },
        )

    async def _get_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_report؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        report_id = self._required_int(
            arguments,
            "report_id",
        )

        report = (
            self._report_query_service
            .get_report(
                report_id
            )
        )

        return ProjectToolResult(
            tool_id="get_report",
            success=True,
            data={
                "report": serialize_report_details(
                    report
                )
            },
        )

    async def _get_latest_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_latest_report؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        report = self._latest_report_for_server(
            server_id
        )

        if report is None:
            return ProjectToolResult(
                tool_id="get_latest_report",
                success=False,
                error_code="report_not_found",
                error_message=(
                    "No report found for server "
                    f"{server_id}."
                ),
            )

        return ProjectToolResult(
            tool_id="get_latest_report",
            success=True,
            data={
                "report": serialize_report_details(
                    report
                )
            },
        )

    def _latest_report_for_server(
        self,
        server_id: int,
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _latest_report_for_server؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        items, total = (
            self._report_query_service
            .list_reports(
                server_id=server_id,
                page=1,
                page_size=1,
            )
        )

        if total < 1 or not items:
            return None

        return (
            self._report_query_service
            .get_report(
                items[0].id
            )
        )
