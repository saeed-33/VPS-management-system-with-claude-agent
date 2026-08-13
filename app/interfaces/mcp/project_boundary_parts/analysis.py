from __future__ import annotations

from typing import Any

from app.interfaces.mcp.schemas import ProjectToolResult
from app.interfaces.mcp.serializers import (
    serialize_analysis,
    serialize_incident_context,
    serialize_knowledge_context,
)


class AnalysisToolsMixin:
    async def _find_exact_report_match(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        normalized = self._normalizer.normalize(
            report
        )
        fingerprint = (
            self._fingerprint_service
            .create(normalized)
        )
        match = (
            self._analysis_repository
            .find_completed_by_fingerprint(
                server_id=report.server_id,
                report_fingerprint=fingerprint,
                exclude_report_id=report_id,
            )
        )

        return ProjectToolResult(
            tool_id="find_exact_report_match",
            success=True,
            data={
                "matched": match is not None,
                "report_fingerprint": fingerprint,
                "analysis": (
                    serialize_analysis(match)
                    if match is not None
                    else None
                ),
            },
        )

    async def _search_similar_incidents(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        return await self._search_incidents(
            tool_id="search_similar_incidents",
            arguments=arguments,
        )

    async def _get_top_similar_reports(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        return await self._search_incidents(
            tool_id="get_top_similar_reports",
            arguments={
                **arguments,
                "limit": min(
                    self._optional_int(
                        arguments,
                        "limit",
                        default=3,
                    ),
                    3,
                ),
            },
        )

    async def _search_incidents(
        self,
        *,
        tool_id: str,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._incident_retriever,
            "incident_retriever",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        limit = min(
            self._optional_int(
                arguments,
                "limit",
                default=3,
            ),
            3,
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        normalized = self._normalizer.normalize(
            report
        )
        command_set_hash = (
            self._normalizer
            .command_set_hash(report)
        )

        contexts = await (
            self._incident_retriever.retrieve(
                normalized_report=normalized,
                server_id=report.server_id,
                monitoring_profile_id=(
                    report.monitoring_profile_id
                ),
                command_set_hash=command_set_hash,
                exclude_report_id=report_id,
            )
        )

        return ProjectToolResult(
            tool_id=tool_id,
            success=True,
            data={
                "limit": limit,
                "similar_reports": [
                    serialize_incident_context(
                        item
                    )
                    for item in contexts[:limit]
                ],
            },
        )

    async def _analyze_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_orchestrator,
            "analysis_orchestrator",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        force = bool(
            arguments.get("force", False)
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        analysis_id = await (
            self._analysis_orchestrator
            .process(
                report_id=report_id,
                server_id=report.server_id,
                force=force,
            )
        )
        analysis = (
            self._analysis_repository
            .get_by_id(analysis_id)
        )

        return ProjectToolResult(
            tool_id="analyze_report",
            success=True,
            data={
                "analysis_id": analysis_id,
                "analysis": (
                    serialize_analysis(analysis)
                    if analysis is not None
                    else None
                ),
            },
        )

    async def _get_analysis(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        analysis = None

        if "analysis_id" in arguments:
            analysis_id = self._required_int(
                arguments,
                "analysis_id",
            )
            analysis = (
                self._analysis_repository
                .get_by_id(analysis_id)
            )
        elif "report_id" in arguments:
            report_id = self._required_int(
                arguments,
                "report_id",
            )
            analysis = (
                self._analysis_repository
                .get_by_report_id(report_id)
            )
        else:
            raise ValueError(
                "analysis_id or report_id is required."
            )

        if analysis is None:
            return ProjectToolResult(
                tool_id="get_analysis",
                success=False,
                error_code="analysis_not_found",
                error_message="Analysis not found.",
            )

        return ProjectToolResult(
            tool_id="get_analysis",
            success=True,
            data={
                "analysis": serialize_analysis(
                    analysis
                )
            },
        )

    async def _search_knowledge(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._knowledge_retriever,
            "knowledge_retriever",
        )

        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string."
            )

        domains = arguments.get("domains", [])
        if not isinstance(domains, list):
            raise ValueError(
                "domains must be a list."
            )

        specialist_slug = arguments.get(
            "specialist_slug"
        )
        if (
            specialist_slug is not None
            and not isinstance(specialist_slug, str)
        ):
            raise ValueError(
                "specialist_slug must be a string."
            )

        limit = min(
            self._optional_int(
                arguments,
                "limit",
                default=6,
            ),
            6,
        )

        contexts = await (
            self._knowledge_retriever.retrieve(
                query=query,
                specialist_slug=specialist_slug,
                domains=tuple(
                    str(item)
                    for item in domains
                ),
            )
        )

        return ProjectToolResult(
            tool_id="search_knowledge",
            success=True,
            data={
                "limit": limit,
                "knowledge": [
                    serialize_knowledge_context(
                        item
                    )
                    for item in contexts[:limit]
                ],
            },
        )
