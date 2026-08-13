import asyncio
import logging
from datetime import UTC, datetime
from typing import Protocol

logger = logging.getLogger(__name__)


class SchedulableServerRecord(Protocol):
    id: int
    interval_seconds: int
    monitor_enabled: bool


class MonitoringRunnerProtocol(Protocol):
    async def run(
        self,
        server_id: int,
    ):
        ...


class SchedulerServerRepositoryProtocol(Protocol):
    def list_enabled_servers(
        self,
    ) -> list[SchedulableServerRecord]:
        ...


class MonitoringScheduler:
    """
    مجدول مراقبة عدة سيرفرات.

    يفحص قاعدة البيانات كل عدة ثوانٍ ويشغّل السيرفرات
    التي انتهت فترة المراقبة الخاصة بها.
    """

    def __init__(
        self,
        *,
        server_repository: (
            SchedulerServerRepositoryProtocol
        ),
        monitoring_service: MonitoringRunnerProtocol,
        polling_interval_seconds: float = 5.0,
        max_concurrent_servers: int = 5,
    ) -> None:
        self._server_repository = server_repository
        self._monitoring_service = monitoring_service

        self._polling_interval_seconds = (
            polling_interval_seconds
        )

        self._stop_event = asyncio.Event()

        self._last_run_at: dict[int, datetime] = {}
        self._running_server_ids: set[int] = set()

        self._semaphore = asyncio.Semaphore(
            max_concurrent_servers
        )

    async def start(self) -> None:
        logger.info(
            "Monitoring scheduler started."
        )

        while not self._stop_event.is_set():
            try:
                await self.run_iteration()

            except Exception:
                logger.exception(
                    "Scheduler iteration failed."
                )

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._polling_interval_seconds,
                )
            except TimeoutError:
                pass

        logger.info(
            "Monitoring scheduler stopped."
        )

    def stop(self) -> None:
        self._stop_event.set()

    async def run_iteration(self) -> None:
        now = datetime.now(UTC)

        servers = (
            self._server_repository
            .list_enabled_servers()
        )

        tasks: list[asyncio.Task[None]] = []

        for server in servers:
            if not self._should_run(server, now):
                continue

            self._last_run_at[server.id] = now

            task = asyncio.create_task(
                self._run_server(server.id)
            )

            tasks.append(task)

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

    def _should_run(
        self,
        server: SchedulableServerRecord,
        now: datetime,
    ) -> bool:
        if not server.monitor_enabled:
            return False

        if server.id in self._running_server_ids:
            return False

        last_run_at = self._last_run_at.get(
            server.id
        )

        if last_run_at is None:
            return True

        elapsed_seconds = (
            now - last_run_at
        ).total_seconds()

        return (
            elapsed_seconds
            >= server.interval_seconds
        )

    async def _run_server(
        self,
        server_id: int,
    ) -> None:
        if server_id in self._running_server_ids:
            return

        self._running_server_ids.add(server_id)

        try:
            async with self._semaphore:
                logger.info(
                    "Monitoring started | server_id=%s",
                    server_id,
                )

                await self._monitoring_service.run(
                    server_id
                )

                logger.info(
                    "Monitoring completed | server_id=%s",
                    server_id,
                )

        except Exception:
            logger.exception(
                "Monitoring cycle failed | server_id=%s",
                server_id,
            )

        finally:
            self._running_server_ids.discard(
                server_id
            )