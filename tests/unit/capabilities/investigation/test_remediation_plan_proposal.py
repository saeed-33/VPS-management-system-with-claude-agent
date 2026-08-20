"""Tests for test remediation plan proposal.
اختبارات انتقال التشخيص المكتمل إلى خطة معالجة مقترحة دون تنفيذ.
"""
from __future__ import annotations

from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.capabilities.remediation.plan_proposal_service import (
    RemediationPlanProposalService,
)
from app.capabilities.remediation.service.remediation_service import RemediationService
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository


def make_proposal_service():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[RemediationPlanModel.__table__])
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    repository = RemediationRepository(factory)
    remediation = RemediationService(repository=repository)
    return RemediationPlanProposalService(
        repository=repository,
        remediation_service=remediation,
    ), repository


def diagnosis(*, actions):
    return SimpleNamespace(
        investigation_id="investigation-1",
        server_id=7,
        summary="A named service is inactive.",
        claims=(SimpleNamespace(claim_id="claim-1"),),
        evidence_ids=("evidence-1",),
        metadata={"recommended_remediation_actions": actions},
    )


def test_completed_investigation_creates_proposed_plan_without_execution():
    service, repository = make_proposal_service()
    plans = service.create_from_diagnosis(
        diagnosis=diagnosis(
            actions=[
                {
                    "action_type": "start_service",
                    "target": "nginx",
                    "reason": "The service is inactive.",
                    "expected_effect": "The service becomes active.",
                    "risk_level": "low",
                    "rollback_supported": True,
                }
            ]
        ),
        server_id=7,
    )

    assert len(plans) == 1
    assert plans[0].status == RemediationPlanStatus.PROPOSED.value
    assert plans[0].proposed_actions[0]["action_type"] == "start_service"
    assert plans[0].approval_status is None
    assert plans[0].execution_status is None
    assert plans[0].plan_metadata["source"] == "completed_investigation"
    assert repository.get_latest_plan_for_investigation("investigation-1") is not None


def test_plan_proposal_is_idempotent_for_same_investigation():
    service, _repository = make_proposal_service()
    diagnosis_value = diagnosis(
        actions=[
            {
                "action_type": "start_service",
                "target": "nginx",
                "reason": "The service is inactive.",
                "expected_effect": "The service becomes active.",
                "risk_level": "low",
                "rollback_supported": True,
            }
        ]
    )

    first = service.create_from_diagnosis(diagnosis=diagnosis_value, server_id=7)
    second = service.create_from_diagnosis(diagnosis=diagnosis_value, server_id=7)

    assert [item.plan_id for item in second] == [first[0].plan_id]


def test_completed_investigation_records_no_solution_when_no_named_action_exists():
    service, _repository = make_proposal_service()
    plans = service.create_from_diagnosis(
        diagnosis=diagnosis(actions=[]),
        server_id=7,
    )

    assert len(plans) == 1
    assert plans[0].status == RemediationPlanStatus.NO_SOLUTION_FOUND.value
    assert plans[0].proposed_actions == []
