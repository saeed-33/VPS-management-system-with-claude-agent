"""نقطة دخول خدمة مراقبة السيرفر وإدارة رحلة التشخيص والمعالجة.

ينشئ هذا الملف تطبيق FastAPI، يهيئ التخزين والخدمات، يستعيد المهام التي انقطعت،
ويبدأ جدولة المراقبة عند توفر مشغل Claude. كما يسجل مسارات الإدارة وفحص الصحة
دون تنفيذ منطق المراقبة أو التشخيص داخل طبقة الدخول نفسها."""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.interfaces.admin.api.agent_observability import router as agent_observability_router
from app.interfaces.admin.api.investigations import router as investigations_router
from app.interfaces.admin.api.commands import router as commands_router
from app.interfaces.admin.api.profiles.router import router as profiles_router
from app.interfaces.admin.api.reports import router as reports_router
from app.interfaces.admin.api.servers import router as servers_router
from app.interfaces.admin.api.specialists import router as specialists_router
from app.interfaces.admin.api.knowledge_sources import router as knowledge_sources_router
from app.interfaces.admin.api.diagnostic_tools import router as diagnostic_tools_router
from app.interfaces.admin.api.system import router as system_router
from app.interfaces.admin.api.remediation import router as remediation_router
from app.interfaces.admin.api.autonomous_remediation import router as autonomous_remediation_router
from app.interfaces.admin.auth.middleware import AdminAuthMiddleware
from app.interfaces.admin.auth.service import AdminAuthService
from app.interfaces.admin.web.auth_routes import router as auth_router
from app.interfaces.admin.web.routes import router as web_router
from app.composition import container
from app.core.config import settings
from app.infrastructure.database.engine import (
    create_database_tables,
)
from app.core.logging import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


APP_DIRECTORY = Path(__file__).resolve().parent

WEB_DIRECTORY = (
    APP_DIRECTORY
    / "interfaces"
    / "admin"
    / "web"
)

STATIC_DIRECTORY = (
    WEB_DIRECTORY
    / "static"
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    يدير بداية التطبيق ونهايته مع الحفاظ على حالة المهام والمعالجات.

    ينشئ جداول التخزين، يغلق المهام والتنفيذات التي انقطعت سابقًا، يبدأ المجدول
    عندما يكون runtime متاحًا، ثم يوقفه بأمان عند إغلاق التطبيق.
    """
    # نهيئ التخزين ونغلق الحالات المعلقة قبل قبول طلبات جديدة من المستخدم.

    logger.info(
        "Application startup started."
    )

    create_database_tables()

    recovered_jobs = (
        container.claude_agent_job_service
        .recover_interrupted_jobs()
    )

    recovered_remediation = (
        container.remediation_service
        .recover_interrupted_executions()
    )

    if recovered_remediation:
        logger.warning(
            "Marked %s interrupted remediation execution(s) for operator review.",
            recovered_remediation,
        )

    if recovered_jobs:
        logger.warning(
            "Recovered %s interrupted Claude agent job(s).",
            recovered_jobs,
        )

    scheduler_task = None
    investigation_backlog_task = None

    if (
        container.claude_supervisor.status["state"]
        == "active"
    ):
        scheduler_task = asyncio.create_task(
            container.scheduler.start(),
            name="monitoring-scheduler",
        )
    else:
        logger.warning(
            "Scheduled monitoring disabled because "
            "the Claude operational runtime is disabled."
        )

    if container.investigation_backlog_worker is not None:
        investigation_backlog_task = asyncio.create_task(
            container.investigation_backlog_worker.start(),
            name="investigation-backlog-worker",
        )

    app.state.scheduler = container.scheduler
    app.state.scheduler_task = scheduler_task
    app.state.investigation_backlog_task = investigation_backlog_task
    app.state.container = container

    logger.info(
        "Application startup completed."
    )

    try:
        yield

    finally:
        logger.info(
            "Application shutdown started."
        )

        if scheduler_task is not None:
            container.scheduler.stop()
            scheduler_task.cancel()

            try:
                await scheduler_task

            except asyncio.CancelledError:
                pass

            except Exception:
                logger.exception(
                    "Scheduler shutdown failed."
                )

        if investigation_backlog_task is not None:
            container.investigation_backlog_worker.stop()
            investigation_backlog_task.cancel()

            try:
                await investigation_backlog_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception(
                    "Investigation backlog worker shutdown failed."
                )

        if container.embedding_client is not None:
            await container.embedding_client.close()

        logger.info(
            "Application shutdown completed."
        )



app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

admin_auth_service = AdminAuthService()
app.state.admin_auth_service = admin_auth_service
app.add_middleware(
    AdminAuthMiddleware,
    auth_service=admin_auth_service,
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIRECTORY)
    ),
    name="static",
)


app.include_router(auth_router)
app.include_router(web_router)
app.include_router(servers_router)
app.include_router(commands_router)
app.include_router(profiles_router)
app.include_router(reports_router)
app.include_router(specialists_router)
app.include_router(knowledge_sources_router)
app.include_router(diagnostic_tools_router)
app.include_router(investigations_router)
app.include_router(system_router)
app.include_router(agent_observability_router)
app.include_router(remediation_router)
app.include_router(autonomous_remediation_router)


@app.get(
    "/health",
    tags=["system"],
)
async def health_check() -> dict:
    """
    يعيد صورة مختصرة عن جاهزية التطبيق لتشغيل المراقبة والتحليل.

    يوضح الرد حالة مشغل Claude والمجدول ومزود التحليل، ولا يدعي أن أي سيرفر
    سليم أو أن تشخيصًا معينًا قد اكتمل.
    """
    supervisor_status = (
        container.claude_supervisor.status
    )
    analysis_enabled = (
        container.analysis_orchestrator
        is not None
    )

    return {
        "status": "ok",
        "application": settings.app_name,
        "monitoring_scheduler": (
            "enabled"
            if supervisor_status["state"] == "active"
            else "disabled"
        ),
        "supervisor": supervisor_status,
        "llm_analysis": {
            "enabled": analysis_enabled,
            "provider": (
                container.report_analyzer.provider_name
                if container.report_analyzer
                is not None
                else None
            ),
            "model": (
                container.report_analyzer.model_name
                if container.report_analyzer
                is not None
                else None
            ),
        },
    }
