# Tests for test backlog worker.
import asyncio
from types import SimpleNamespace

from app.capabilities.investigation.backlog_worker import (
    InvestigationBacklogWorker,
)


class Repository:
    def __init__(self, model):
        self.model = model

    def list_recoverable(self, *, limit):
        assert limit == 1
        return [self.model]


class ClosingRepository(Repository):
    def __init__(self, model):
        super().__init__(model)
        self.closed = []

    def promote_next_candidate(self, *, investigation_id):
        return None

    def close_without_evidence(self, *, investigation_id):
        self.closed.append(investigation_id)


class ReadService:
    def __init__(self, detail):
        self.detail = detail

    def get(self, investigation_id):
        assert investigation_id == self.detail.investigation_id
        return self.detail


class AnalysisRepository:
    def __init__(self, analysis):
        self.analysis = analysis

    def get_by_id(self, analysis_id):
        return self.analysis


class Registry:
    def __init__(self, specialist):
        self.specialist = specialist

    def snapshot(self):
        return SimpleNamespace(
            get_by_slug=lambda slug: (
                self.specialist
                if slug == self.specialist.slug
                else None
            )
        )


class Loop:
    def __init__(self):
        self.calls = []

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        return "loop-result"


class ExecutionService:
    def __init__(self):
        self.reservations = []
        self.finalized = []

    def reserve_with_token(self, **kwargs):
        self.reservations.append(kwargs)
        return {
            "status": "reserved",
            "ownership_token": "token-1",
            "actions_used": 0,
        }

    async def finalize(self, **kwargs):
        self.finalized.append(kwargs)
        return {"status": "persisted"}

    async def finalize_failure(self, **kwargs):
        raise AssertionError("failure finalizer must not be called")


def make_worker():
    specialist = SimpleNamespace(
        id=7,
        slug="cpu",
        knowledge_topics=("cpu",),
    )
    candidate = SimpleNamespace(
        specialist_slug="cpu",
        is_selected=True,
        matched_issue_indexes=(0,),
    )
    detail = SimpleNamespace(
        investigation_id="investigation-1",
        should_investigate=True,
        analysis_id=4,
        report_id=9,
        server_id=3,
        candidates=(candidate,),
        max_specialists=2,
        max_rounds=2,
        max_actions=4,
        detected_domains=("cpu",),
    )
    model = SimpleNamespace(investigation_id=detail.investigation_id)
    loop = Loop()
    execution = ExecutionService()
    worker = InvestigationBacklogWorker(
        investigation_repository=Repository(model),
        investigation_read_service=ReadService(detail),
        analysis_repository=AnalysisRepository(
            SimpleNamespace(
                summary="CPU is saturated.",
                issues=[{"severity": "critical"}],
            )
        ),
        specialist_registry=Registry(specialist),
        specialist_investigation_loop=loop,
        specialist_execution_service=execution,
    )
    return worker, loop, execution


def test_worker_recovers_one_selected_specialist():
    worker, loop, execution = make_worker()

    recovered = asyncio.run(worker.run_iteration())

    assert recovered == 1
    assert len(loop.calls) == 1
    assert loop.calls[0]["task"].metadata["source"] == (
        "investigation_backlog_worker"
    )
    assert execution.reservations[0]["specialist_slug"] == "cpu"
    assert execution.finalized[0]["ownership_token"] == "token-1"


def test_worker_does_nothing_when_specialist_runtime_is_unavailable():
    worker, _, _ = make_worker()
    worker._specialist_investigation_loop = None

    assert asyncio.run(worker.run_iteration()) == 0


def test_worker_closes_waiting_investigation_when_candidates_are_exhausted():
    specialist = SimpleNamespace(
        specialist_slug="cpu",
        is_selected=True,
    )
    detail = SimpleNamespace(
        investigation_id="investigation-1",
        should_investigate=True,
        candidates=(specialist,),
        runtime=SimpleNamespace(
            specialist_runs=(
                {"specialist_slug": "cpu", "status": "completed", "findings": []},
            )
        ),
    )
    repository = ClosingRepository(SimpleNamespace(investigation_id="investigation-1"))
    worker = InvestigationBacklogWorker(
        investigation_repository=repository,
        investigation_read_service=ReadService(detail),
        analysis_repository=None,
        specialist_registry=None,
        specialist_investigation_loop=object(),
        specialist_execution_service=None,
    )

    asyncio.run(worker._resume("investigation-1"))

    assert repository.closed == ["investigation-1"]


def test_completed_run_without_findings_requires_candidate_promotion():
    detail = SimpleNamespace(
        candidates=(SimpleNamespace(specialist_slug="cpu", is_selected=True),),
        runtime=SimpleNamespace(
            specialist_runs=(
                {"specialist_slug": "cpu", "status": "completed", "findings": []},
            )
        ),
    )

    assert InvestigationBacklogWorker._needs_candidate_promotion(detail) is True
