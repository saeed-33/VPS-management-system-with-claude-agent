import asyncio
import logging

from app.agent.analysis.analysis_orchestrator import (
    AnalysisOrchestrator,
)
from app.agent.analysis.server_analysis_agent import (
    ServerAnalysisAgent,
)
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
)


logger = logging.getLogger(__name__)


class AnalysisAgentManager:
    """
    ينشئ وكيل تحليل فرعيًا واحدًا لكل سيرفر عند الحاجة.
    """

    def __init__(
        self,
        *,
        analysis_orchestrator: AnalysisOrchestrator,
        analysis_repository: AnalysisRepository,
        queue_size_per_server: int = 100,
    ) -> None:
        self._analysis_orchestrator = (
            analysis_orchestrator
        )

        self._analysis_repository = (
            analysis_repository
        )

        self._queue_size_per_server = (
            queue_size_per_server
        )

        self._agents: dict[
            int,
            ServerAnalysisAgent,
        ] = {}

        self._lock = asyncio.Lock()
        self._stopping = False

    async def enqueue_report(
        self,
        *,
        server_id: int,
        report_id: int,
        force: bool = False,
    ) -> None:
        if self._stopping:
            raise RuntimeError(
                "Analysis agent manager is stopping."
            )

        agent = await self._get_or_create_agent(
            server_id
        )

        await agent.enqueue(
            report_id=report_id,
            force=force,
        )

    async def recover_pending_jobs(
        self,
    ) -> None:
        """
        يعيد جدولة التحليلات التي كانت pending أو running
        عند توقف التطبيق السابق.
        """

        pending_analyses = (
            self._analysis_repository
            .list_pending_or_running()
        )

        for analysis in pending_analyses:
            self._analysis_repository.reset_for_retry(
                analysis.id
            )

            await self.enqueue_report(
                server_id=analysis.server_id,
                report_id=analysis.report_id,
                force=False,
            )

        if pending_analyses:
            logger.info(
                "Recovered pending analysis jobs | "
                "count=%s",
                len(pending_analyses),
            )

    async def stop_all(
        self,
        *,
        drain: bool = True,
    ) -> None:
        self._stopping = True

        agents = list(
            self._agents.values()
        )

        if agents:
            await asyncio.gather(
                *(
                    agent.stop(drain=drain)
                    for agent in agents
                ),
                return_exceptions=True,
            )

        self._agents.clear()

    async def _get_or_create_agent(
        self,
        server_id: int,
    ) -> ServerAnalysisAgent:
        existing = self._agents.get(
            server_id
        )

        if existing is not None:
            return existing

        async with self._lock:
            existing = self._agents.get(
                server_id
            )

            if existing is not None:
                return existing

            agent = ServerAnalysisAgent(
                server_id=server_id,
                analysis_orchestrator=(
                    self._analysis_orchestrator
                ),
                queue_size=(
                    self._queue_size_per_server
                ),
            )

            agent.start()

            self._agents[server_id] = agent

            return agent