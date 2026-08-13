from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.runtime.claude import (
    ClaudeAgentJobService,
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
    ClaudeStructuredOutput,
)
from app.infrastructure.database.models.agent_job import (
    AgentJobModel,
)
from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)


def make_repository():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    AgentJobModel.__table__.create(
        engine
    )
    factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    return AgentJobRepository(
        factory
    ), factory


def make_request(
    job_id="job-1",
) -> ClaudeRuntimeRequest:
    return ClaudeRuntimeRequest(
        job_id=job_id,
        job_type="monitoring_cycle",
        prompt="Run fixed workflow.",
        context={
            "server_id": 7,
        },
        max_turns=4,
        metadata={
            "source": "test",
        },
    )


def test_job_is_created_from_runtime_request():
    repository, _ = make_repository()
    service = ClaudeAgentJobService(
        repository
    )

    model = service.create_from_request(
        make_request(),
        server_id=7,
    )

    assert model.job_id == "job-1"
    assert model.job_type == "monitoring_cycle"
    assert model.server_id == 7
    assert model.status == "queued"
    assert model.job_metadata["context"] == {
        "server_id": 7,
    }
    assert model.job_metadata["max_turns"] == 4
    assert model.job_metadata["source"] == "test"


def test_job_completion_preserves_result_observability():
    repository, _ = make_repository()
    service = ClaudeAgentJobService(
        repository
    )
    service.create_from_request(
        make_request()
    )

    result = ClaudeRuntimeResult(
        job_id="job-1",
        job_type="monitoring_cycle",
        status=ClaudeJobStatus.COMPLETED,
        session_id="session-1",
        structured_output=ClaudeStructuredOutput(
            status=ClaudeJobStatus.COMPLETED,
            summary="Done.",
            data={
                "report_id": 123,
            },
        ),
        turn_count=3,
        tool_call_count=2,
        usage_metadata={
            "tokens": 99,
        },
    )

    model = service.complete_from_result(
        result
    )

    assert model.status == "completed"
    assert model.claude_session_id == "session-1"
    assert model.completed_at is not None
    assert model.error_code is None
    assert model.turn_count == 3
    assert model.tool_call_count == 2
    assert model.usage_metadata == {
        "tokens": 99,
    }


def test_job_survives_repository_recreation():
    repository, factory = make_repository()
    ClaudeAgentJobService(
        repository
    ).create_from_request(
        make_request(
            "job-survives"
        )
    )

    reloaded_repository = AgentJobRepository(
        factory
    )
    model = (
        reloaded_repository
        .get_by_job_id(
            "job-survives"
        )
    )

    assert model is not None
    assert model.status == "queued"


def test_interrupted_jobs_are_recovered_as_failed():
    repository, _ = make_repository()
    service = ClaudeAgentJobService(
        repository
    )
    service.create_from_request(
        make_request("queued-job")
    )
    service.create_from_request(
        make_request("running-job")
    )
    service.mark_running(
        job_id="running-job",
        session_id="session-running",
    )

    recovered = (
        service.recover_interrupted_jobs()
    )

    assert recovered == 2

    queued = repository.get_by_job_id(
        "queued-job"
    )
    running = repository.get_by_job_id(
        "running-job"
    )

    assert queued.status == "failed"
    assert running.status == "failed"
    assert (
        queued.error_code
        == "interrupted_after_restart"
    )
    assert running.completed_at is not None


def test_recent_jobs_can_be_filtered_by_status():
    repository, _ = make_repository()
    service = ClaudeAgentJobService(
        repository
    )
    service.create_from_request(
        make_request("job-a"),
        server_id=1,
    )
    service.create_from_request(
        make_request("job-b"),
        server_id=2,
    )
    service.recover_interrupted_jobs()

    failed_for_server_two = (
        repository.list_recent(
            server_id=2,
            status="failed",
        )
    )

    assert [
        job.job_id
        for job in failed_for_server_two
    ] == ["job-b"]
