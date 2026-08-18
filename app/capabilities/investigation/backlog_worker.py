"""
عامل استرداد التحقيقات التي توقفت بعد حفظ قرار التوجيه.

يعيد تشغيل التحقيقات القابلة للاسترداد بحدود صغيرة، ويحترم حجز المتخصص
حتى لا يتنافس مع جلسة Claude أو يعيد تنفيذ الأثر نفسه.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.core.contracts.investigation import (
    InvestigationBudget,
    SpecialistTask,
    SpecialistTaskStatus,
)


logger = logging.getLogger(__name__)


class InvestigationBacklogWorker:
    """
    يستأنف تحقيقاً واحداً قابلاً للاسترداد في كل دورة.

    لا يلتقط التحقيقات المرتبطة بسيرفر متوقف؛ يعيد المستودع هذه الحماية حتى
    لا يحاول العامل جمع أدلة من سيرفر أوقفه المشغل عمداً.
    """

    def __init__(
        self,
        *,
        investigation_repository,
        investigation_read_service,
        analysis_repository,
        specialist_registry,
        specialist_investigation_loop,
        specialist_execution_service,
        polling_interval_seconds: float = 15.0,
    ) -> None:
        if polling_interval_seconds < 5.0:
            raise ValueError(
                "polling_interval_seconds must be >= 5.0."
            )

        self._investigation_repository = investigation_repository
        self._investigation_read_service = investigation_read_service
        self._analysis_repository = analysis_repository
        self._specialist_registry = specialist_registry
        self._specialist_investigation_loop = (
            specialist_investigation_loop
        )
        self._specialist_execution_service = specialist_execution_service
        self._polling_interval_seconds = polling_interval_seconds
        self._stop_event = asyncio.Event()
        self._iteration_lock = asyncio.Lock()

    async def start(self) -> None:
        """يشغل العامل حتى يطلب التطبيق إيقافه."""
        logger.info("Investigation backlog worker started.")

        while not self._stop_event.is_set():
            try:
                await self.run_iteration()
            except Exception:
                logger.exception("Investigation backlog iteration failed.")

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._polling_interval_seconds,
                )
            except TimeoutError:
                pass

        logger.info("Investigation backlog worker stopped.")

    def stop(self) -> None:
        """يطلب إنهاء العامل دون إلغاء التحقيق الجاري قسراً."""
        self._stop_event.set()

    async def run_iteration(self) -> int:
        """يستأنف تحقيقاً واحداً ويعيد عدد التحقيقات التي بدأ استردادها."""
        if self._specialist_investigation_loop is None:
            return 0

        async with self._iteration_lock:
            pending = self._investigation_repository.list_recoverable(
                limit=1
            )
            if not pending:
                return 0

            model = pending[0]
            await self._resume(model.investigation_id)
            return 1

    @staticmethod
    def _needs_candidate_promotion(detail: Any) -> bool:
        """
        يحدد إن كانت الموجة الحالية انتهت بلا أدلة وتحتاج مرشحاً جديداً.
        """
        selected = tuple(
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        )
        if not selected:
            return True

        runtime = getattr(detail, "runtime", None)
        if runtime is None:
            return False
        runs = tuple(runtime.specialist_runs or ())
        terminal_statuses = {"completed", "failed", "cancelled"}
        by_slug = {
            item.get("specialist_slug"): item
            for item in runs
            if item.get("specialist_slug")
        }
        if not all(
            by_slug.get(slug, {}).get("status") in terminal_statuses
            for slug in selected
        ):
            return False
        return not any(
            bool(item.get("findings"))
            for item in by_slug.values()
            if item.get("status") == "completed"
        )

    async def _resume(self, investigation_id: str) -> None:
        detail = self._investigation_read_service.get(investigation_id)
        if detail is None or not detail.should_investigate:
            return

        if self._needs_candidate_promotion(detail):
            promoted = self._investigation_repository.promote_next_candidate(
                investigation_id=investigation_id
            )
            if promoted is None:
                self._investigation_repository.close_without_evidence(
                    investigation_id=investigation_id
                )
                logger.info(
                    "Investigation closed without evidence after candidate "
                    "exhaustion | investigation_id=%s",
                    investigation_id,
                )
                return
            detail = self._investigation_read_service.get(investigation_id)
            if detail is None or not detail.should_investigate:
                return

        analysis = (
            self._analysis_repository.get_by_id(detail.analysis_id)
            if detail.analysis_id is not None
            else None
        )
        if analysis is None:
            analysis = self._analysis_repository.get_by_report_id(
                detail.report_id
            )
        if analysis is None:
            logger.warning(
                "Skipping recoverable investigation without analysis | "
                "investigation_id=%s",
                investigation_id,
            )
            return

        selected_slugs = tuple(
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        )
        if not selected_slugs:
            logger.warning(
                "Skipping recoverable investigation without selected "
                "specialist | investigation_id=%s",
                investigation_id,
            )
            return

        snapshot = self._specialist_registry.snapshot()

        for candidate in detail.candidates:
            if not candidate.is_selected:
                continue

            specialist = snapshot.get_by_slug(candidate.specialist_slug)
            if specialist is None:
                logger.warning(
                    "Skipping unavailable specialist during investigation "
                    "recovery | investigation_id=%s | specialist=%s",
                    investigation_id,
                    candidate.specialist_slug,
                )
                continue

            reservation = self._specialist_execution_service.reserve_with_token(
                investigation_id=investigation_id,
                specialist_slug=specialist.slug,
            )
            reservation_status = reservation.get("status")
            if reservation_status in {"completed", "in_progress"}:
                continue
            if reservation_status != "reserved":
                logger.warning(
                    "Specialist recovery was not reserved | "
                    "investigation_id=%s | specialist=%s | status=%s",
                    investigation_id,
                    specialist.slug,
                    reservation_status,
                )
                continue

            task = SpecialistTask(
                task_id=(
                    f"{investigation_id}:{specialist.slug}:recovery"
                ),
                investigation_id=investigation_id,
                server_id=detail.server_id,
                report_id=detail.report_id,
                specialist_id=specialist.slug,
                objective=(
                    "Resume the persisted investigation for the selected "
                    "specialist. Use the stored analysis as the starting "
                    "point and collect only authorized evidence."
                ),
                trigger_issue_ids=tuple(
                    str(index)
                    for index in candidate.matched_issue_indexes
                ),
                knowledge_topics=specialist.knowledge_topics,
                status=SpecialistTaskStatus.RUNNING,
                metadata={
                    "source": "investigation_backlog_worker",
                    "specialist_definition_id": specialist.id,
                },
            )

            try:
                result = await self._specialist_investigation_loop.run(
                    task=task,
                    specialist=specialist,
                    investigation_budget=InvestigationBudget(
                        max_specialists=detail.max_specialists,
                        max_rounds=detail.max_rounds,
                        max_actions=detail.max_actions,
                    ),
                    detected_domains=detail.detected_domains,
                    initial_analysis_summary=analysis.summary or "",
                    initial_analysis_issues=tuple(analysis.issues or ()),
                    allowed_specialist_slugs=selected_slugs,
                    investigation_actions_used=int(
                        reservation.get("actions_used") or 0
                    ),
                )
            except Exception as exc:
                await self._specialist_execution_service.finalize_failure(
                    task=task,
                    reason=str(exc),
                    selected_specialists=selected_slugs,
                    ownership_token=reservation["ownership_token"],
                )
                logger.exception(
                    "Recovered investigation specialist failed | "
                    "investigation_id=%s | specialist=%s",
                    investigation_id,
                    specialist.slug,
                )
                continue

            await self._specialist_execution_service.finalize(
                task=task,
                loop_result=result,
                selected_specialists=selected_slugs,
                ownership_token=reservation["ownership_token"],
            )
            logger.info(
                "Recovered investigation specialist | "
                "investigation_id=%s | specialist=%s",
                investigation_id,
                specialist.slug,
            )


__all__ = ["InvestigationBacklogWorker"]
