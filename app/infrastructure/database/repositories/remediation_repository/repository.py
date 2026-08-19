"""
خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع.
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.contracts.remediation.approval_status import ApprovalStatus
from app.core.contracts.remediation.create_remediation_plan_dto import CreateRemediationPlanDTO
from app.core.contracts.remediation.create_sandbox_result_dto import CreateSandboxResultDTO
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.core.contracts.remediation.remediation_risk import RemediationRisk
from app.core.contracts.remediation.rollback_status import RollbackStatus
from app.core.contracts.remediation.helpers import remediation_fingerprint
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation.approval import RemediationApprovalModel
from app.infrastructure.database.models.remediation.audit_event import RemediationAuditEventModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.sandbox_result import RemediationSandboxResultModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.models.remediation.sandbox_validation import SandboxValidationModel
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal

from .execution_operations import _ExecutionOperationsMixin
from .plan_operations import _PlanOperationsMixin
from .sandbox_operations import _SandboxOperationsMixin


class RemediationRepository(_PlanOperationsMixin, _SandboxOperationsMixin, _ExecutionOperationsMixin):
    """
    مسؤول عن كل سجل ينتج من خطة المعالجة حتى التحقق أو التراجع والتدقيق.
    """

    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        يهيئ مستودع خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
