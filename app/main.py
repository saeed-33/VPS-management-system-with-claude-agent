import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.interfaces.admin.api import (
    agent_observability_router,
    investigations_router,
    commands_router,
    profiles_router,
    reports_router,
    servers_router,
    specialists_router,
    knowledge_sources_router,
    diagnostic_tools_router,
    system_router,
    remediation_router,
)
from app.interfaces.admin.web import router as web_router
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
    # Application lifecycle after C.14.9:
    # - create database tables;
    # - start periodic scheduling only when the Claude runtime is active;
    # - no Python analysis-agent queue recovery or draining.

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
app.include_router(specialists_router)
app.include_router(knowledge_sources_router)
app.include_router(diagnostic_tools_router)
app.include_router(investigations_router)
app.include_router(system_router)
app.include_router(agent_observability_router)
app.include_router(remediation_router)


@app.get(
    "/health",
    tags=["system"],
)
async def health_check() -> dict:
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
