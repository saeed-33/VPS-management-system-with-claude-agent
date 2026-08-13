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
    async def _get_server_context(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
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
