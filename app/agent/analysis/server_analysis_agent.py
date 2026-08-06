import asyncio
import logging
from dataclasses import dataclass

from app.agent.analysis.analysis_orchestrator import (
    AnalysisOrchestrator,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class AnalysisJob:
    server_id: int
    report_id: int
    force: bool = False


class ServerAnalysisAgent:
    """
    وكيل فرعي مخصص لسيرفر واحد.

    يستهلك تقارير السيرفر بالتسلسل، مما يمنع تحليل
    تقريرين للسيرفر نفسه في الوقت ذاته.
    """

    def __init__(
        self,
        *,
        server_id: int,
        analysis_orchestrator: AnalysisOrchestrator,
        queue_size: int = 100,
    ) -> None:
        self.server_id = server_id

        self._analysis_orchestrator = (
            analysis_orchestrator
        )

        self._queue: asyncio.Queue[
            AnalysisJob | None
        ] = asyncio.Queue(
            maxsize=queue_size
        )

        self._task: asyncio.Task[None] | None = None
        self._stopping = False

    @property
    def is_running(self) -> bool:
        return (
            self._task is not None
            and not self._task.done()
        )

    @property
    def pending_jobs(self) -> int:
        return self._queue.qsize()

    def start(self) -> None:
        if self.is_running:
            return

        self._stopping = False

        self._task = asyncio.create_task(
            self._worker_loop(),
            name=(
                f"analysis-agent-server-"
                f"{self.server_id}"
            ),
        )

        logger.info(
            "Server analysis agent started | "
            "server_id=%s",
            self.server_id,
        )

    async def enqueue(
        self,
        *,
        report_id: int,
        force: bool = False,
    ) -> None:
        if self._stopping:
            raise RuntimeError(
                "Analysis agent is stopping."
            )

        if not self.is_running:
            self.start()

        await self._queue.put(
            AnalysisJob(
                server_id=self.server_id,
                report_id=report_id,
                force=force,
            )
        )

        logger.info(
            "Report queued for analysis | "
            "server_id=%s | report_id=%s | "
            "queue_size=%s",
            self.server_id,
            report_id,
            self._queue.qsize(),
        )

    async def stop(
        self,
        *,
        drain: bool = True,
    ) -> None:
        self._stopping = True

        if self._task is None:
            return

        if drain:
            await self._queue.join()

        await self._queue.put(None)

        try:
            await self._task
        finally:
            self._task = None

        logger.info(
            "Server analysis agent stopped | "
            "server_id=%s",
            self.server_id,
        )

    async def _worker_loop(self) -> None:
        while True:
            job = await self._queue.get()

            try:
                if job is None:
                    return

                await self._analysis_orchestrator.process(
                    report_id=job.report_id,
                    server_id=job.server_id,
                    force=job.force,
                )

            except asyncio.CancelledError:
                raise

            except Exception:
                # تم حفظ الفشل في قاعدة البيانات
                # داخل ReportAnalyzer.
                logger.exception(
                    "Sub-agent analysis job failed | "
                    "server_id=%s | report_id=%s",
                    self.server_id,
                    (
                        job.report_id
                        if job is not None
                        else None
                    ),
                )

            finally:
                self._queue.task_done()