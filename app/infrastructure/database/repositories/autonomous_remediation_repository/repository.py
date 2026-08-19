"""
سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError

from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation.autonomous_history_snapshot import AutonomousHistorySnapshot
from app.core.contracts.autonomous_remediation.autonomous_policy_decision import AutonomousPolicyDecision
from app.core.contracts.autonomous_remediation.autonomous_policy_status import AutonomousPolicyStatus
from app.core.contracts.autonomous_remediation.autonomous_remediation_policy import AutonomousRemediationPolicy
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation.autonomous_authorization import AutonomousAuthorizationModel
from app.infrastructure.database.models.remediation.autonomous_decision import AutonomousPolicyDecisionModel
from app.infrastructure.database.models.remediation.autonomous_reservation import AutonomousPolicyExecutionReservationModel
from app.infrastructure.database.models.remediation.autonomous_runtime import AutonomousPolicyRuntimeStateModel
from app.infrastructure.database.models.remediation.autonomous_audit_event import AutonomousPolicyAuditEventModel
from app.infrastructure.database.models.remediation.autonomous_policy import AutonomousRemediationPolicyModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.session import SessionLocal

from .decision_history import _DecisionHistoryMixin
from .policy_operations import _PolicyOperationsMixin
from .reservation_operations import _ReservationOperationsMixin
from .runtime_state import _RuntimeStateMixin


class AutonomousRemediationRepository(_PolicyOperationsMixin, _DecisionHistoryMixin, _ReservationOperationsMixin, _RuntimeStateMixin):
    """
    مسؤول عن السجل الدائم لسياسات المعالجة الذاتية وقراراتها وحجوزها وتاريخها.
    """

    def __init__(self, session_factory=SessionLocal) -> None:
        """
        يهيئ مستودع سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
