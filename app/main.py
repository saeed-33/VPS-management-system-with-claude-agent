import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.api import (
    commands_router,
    profiles_router,
    reports_router,
    servers_router,
)
from app.admin.web import router as web_router
from app.bootstrap import container
from app.shared.config import settings
from app.shared.database.engine import (
    create_database_tables,
)
from app.shared.logging import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


APP_DIRECTORY = Path(__file__).resolve().parent

WEB_DIRECTORY = (
    APP_DIRECTORY
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
    يدير دورة حياة التطبيق.

    عند التشغيل:
    - ينشئ الجداول الناقصة.
    - يستعيد مهام تحليل LLM غير المكتملة.
    - يشغل مجدول المراقبة.

    عند الإغلاق:
    - يوقف المجدول.
    - ينتظر مهام التحليل الموجودة في Queue.
    """

    logger.info(
        "Application startup started."
    )

    create_database_tables()

    if (
        container.analysis_agent_manager
        is not None
    ):
        try:
            await (
                container.analysis_agent_manager
                .recover_pending_jobs()
            )

        except Exception:
            logger.exception(
                "Failed to recover pending "
                "analysis jobs."
            )

    scheduler_task = asyncio.create_task(
        container.scheduler.start(),
        name="monitoring-scheduler",
    )

    app.state.scheduler = container.scheduler
    app.state.scheduler_task = scheduler_task
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

        if (
            container.analysis_agent_manager
            is not None
        ):
            try:
                await (
                    container.analysis_agent_manager
                    .stop_all(
                        drain=True
                    )
                )

            except Exception:
                logger.exception(
                    "Analysis agents shutdown failed."
                )

        logger.info(
            "Application shutdown completed."
        )


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIRECTORY)
    ),
    name="static",
)


app.include_router(web_router)
app.include_router(servers_router)
app.include_router(commands_router)
app.include_router(profiles_router)
app.include_router(reports_router)


@app.get(
    "/health",
    tags=["system"],
)
async def health_check() -> dict:
    analysis_enabled = (
        container.analysis_agent_manager
        is not None
    )

    return {
        "status": "ok",
        "application": settings.app_name,
        "monitoring_scheduler": "enabled",
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