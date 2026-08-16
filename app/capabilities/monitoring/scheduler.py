"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import asyncio
import logging
from datetime import UTC, datetime
from typing import Protocol

logger = logging.getLogger(__name__)


class SchedulableServerRecord(Protocol):
    """
    يمثل SchedulableServerRecord مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    interval_seconds: int
    monitor_enabled: bool


class MonitoringRunnerProtocol(Protocol):
    """
    يمثل MonitoringRunnerProtocol مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def run(
        self,
        server_id: int,
    ):
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class SchedulerServerRepositoryProtocol(Protocol):
    """
    يمثل SchedulerServerRepositoryProtocol مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def list_enabled_servers(
        self,
    ) -> list[SchedulableServerRecord]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_enabled_servers؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[SchedulableServerRecord] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_repository، monitoring_service، polling_interval_seconds، max_concurrent_servers.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى start؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى stop؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._stop_event.set()

    async def run_iteration(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى run_iteration؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        now = datetime.now(UTC)

        servers = (
            self._server_repository
            .list_enabled_servers()
        )

        # scheduler يختار المرشحين فقط؛ تنفيذ دورة كل server يبقى داخل
        # MonitoringService، بينما semaphore يحد concurrency على مستوى الجدولة.

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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _should_run؛ المدخلات المهمة: server، now.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _run_server؛ المدخلات المهمة: server_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
