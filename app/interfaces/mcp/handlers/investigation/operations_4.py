"""
معالجات أدوات التحقيق في MCP.

تبدأ التحقيق وتقرأ حالته وأدلته واختصاصييه، وتنفذ اختصاصيًا أو تعرض تقدمه
مع إبقاء دورة التحقيق داخل خدمات المجال.
"""
from __future__ import annotations

from typing import Any

from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus
from app.interfaces.mcp.schemas.result import ProjectToolResult
from app.interfaces.mcp.serializers import (
    serialize_specialist_definition,
    serialize_specialist_loop_result,
    serialize_value,
)


class _InvestigationToolsOperations4:
    """ينظم مجموعة من عمليات التحقيق في MCP."""

    def _specialist_progress(self, detail):
        """
        يعيد تقدم تنفيذ اختصاصي داخل حلقة التحقيق.
        """
        selected = [
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        ]
        metadata = (
            detail.runtime.metadata or {}
            if detail.runtime is not None
            else {}
        )
        completed = list(metadata.get("completed_specialists", ()))
        failed = list(metadata.get("failed_specialists", ()))
        terminal = set(completed) | set(failed)
        return {
            "selected_specialists": list(metadata.get("selected_specialists", selected)),
            "completed_specialists": completed,
            "failed_specialists": failed,
            "remaining_specialists": list(
                metadata.get(
                    "remaining_specialists",
                    [slug for slug in selected if slug not in terminal],
                )
            ),
            "runtime_available": bool(detail.runtime_available),
            "final_diagnosis_available": bool(detail.final_diagnosis_available),
            "status": detail.status,
        }

    def _specialist_by_slug(
        self,
        arguments: dict[str, Any],
    ):
        """
        يبحث عن اختصاصي بمعرفه النصي المطبع.
        """
        self._require_dependency(
            self._specialist_registry,
            "specialist_registry",
        )

        slug = arguments.get(
            "specialist_slug"
        )
        if not isinstance(slug, str) or not slug.strip():
            raise ValueError(
                "specialist_slug must be a non-empty string."
            )

        return (
            self._specialist_registry
            .snapshot()
            .get_by_slug(slug)
        )

    def _read_investigation(
        self,
        arguments: dict[str, Any],
    ):
        """
        يقرأ التحقيق من خدمة المجال ويعيد تمثيله القابل للتسلسل.
        """
        self._require_dependency(
            self._investigation_read_service,
            "investigation_read_service",
        )

        investigation_id = arguments.get(
            "investigation_id"
        )
        if (
            not isinstance(investigation_id, str)
            or not investigation_id.strip()
        ):
            raise ValueError(
                "investigation_id must be a non-empty string."
            )

        return self._investigation_read_service.get(
            investigation_id.strip()
        )
