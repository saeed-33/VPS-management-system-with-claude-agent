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


class _AutonomousRemediationRepositoryMixin1:
    """ينظم مجموعة من عمليات المستودع."""

    def create_policy(self, policy: AutonomousRemediationPolicy):
        """
        ينشئ أو يحدث سجلًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = self._policy_model(policy)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_policy(self, policy_id: str):
        """
        يسترجع سجلًا من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousRemediationPolicyModel).where(AutonomousRemediationPolicyModel.policy_id == policy_id))

    def find_duplicate_policy(self, policy: AutonomousRemediationPolicy):
        """
        يبحث عن سياسة لها نفس نطاق المشكلة والفعل والهدف ونطاق السيرفرات.

        اختلاف المعرف أو الاسم لا يجعل السياسة مختلفة تشغيلياً؛ وجود أكثر من
        نسخة مطابقة يسبب تطابقات متعددة ورفضاً احترازياً للتنفيذ الذاتي.
        """
        with self._session_factory() as session:
            candidates = session.scalars(
                select(AutonomousRemediationPolicyModel).where(
                    AutonomousRemediationPolicyModel.issue_fingerprint == policy.issue_fingerprint,
                    AutonomousRemediationPolicyModel.allowed_action_type == policy.allowed_action_type,
                    AutonomousRemediationPolicyModel.allowed_target_pattern == policy.allowed_target_pattern,
                )
            ).all()
            policy_servers = tuple(policy.allowed_server_ids or ())
            policy_tags = tuple(policy.allowed_server_tags or ())
            for candidate in candidates:
                if (
                    tuple(candidate.allowed_server_ids or ()) == policy_servers
                    and tuple(candidate.allowed_server_tags or ()) == policy_tags
                ):
                    return candidate
            return None

    def list_policies(self, *, status: str | None = None):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousRemediationPolicyModel).order_by(AutonomousRemediationPolicyModel.created_at.desc())
            if status:
                statement = statement.where(AutonomousRemediationPolicyModel.status == status)
            return list(session.scalars(statement).all())

    def matching_policies(self, *, issue_fingerprint: str, action_type: str, target: str, server_id: int | None):
        """
        يبحث داخل سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها عن سجلات تطابق الحالة أو البصمة أو الشروط المقدمة.
        """
        with self._session_factory() as session:
            statement = select(AutonomousRemediationPolicyModel).where(
                AutonomousRemediationPolicyModel.issue_fingerprint == issue_fingerprint,
                AutonomousRemediationPolicyModel.allowed_action_type == action_type,
            )
            models = list(session.scalars(statement).all())
            return [
                item for item in models
                if not item.allowed_server_ids or server_id in (item.allowed_server_ids or [])
                if item.allowed_target_pattern == target
            ]

    def candidate_keys(self):
        """
        يستخرج مفاتيح الحالات التي تملك سجلًا تاريخيًا يمكن أن تقارن به السياسة.
        """
        with self._session_factory() as session:
            plans = list(session.scalars(select(RemediationPlanModel)).all())
            executions = list(session.scalars(select(RemediationExecutionModel)).all())
            execution_ids = [item.execution_id for item in executions]
            verified_ids = {
                item.execution_id for item in session.scalars(
                    select(RemediationVerificationModel).where(
                        RemediationVerificationModel.status == "verified",
                        RemediationVerificationModel.execution_id.in_(execution_ids),
                    )
                ).all()
            } if execution_ids else set()
            rollback_failures = {
                item.execution_id for item in session.scalars(
                    select(RemediationRollbackModel).where(
                        RemediationRollbackModel.status == "failed",
                        RemediationRollbackModel.execution_id.in_(execution_ids),
                    )
                ).all()
            } if execution_ids else set()
            result = {}
            for plan in plans:
                issue = (plan.plan_metadata or {}).get("issue_fingerprint")
                if not isinstance(issue, str) or not issue.strip():
                    continue
                for execution in executions:
                    if execution.plan_id != plan.plan_id:
                        continue
                    action = next(
                        (item for item in (plan.proposed_actions or []) if item.get("id", item.get("action_id")) == execution.action_id),
                        None,
                    )
                    if action is None:
                        continue
                    target = str(action.get("target") or action.get("service") or "")
                    action_type = str(action.get("action_type") or action.get("type") or action.get("tool") or "")
                    key = (issue, action_type, target)
                    result.setdefault(key, {"executions": [], "plan_ids": set(), "verified_ids": set(), "rollback_failure_ids": set()})
                    result[key]["executions"].append(execution)
                    result[key]["plan_ids"].add(plan.plan_id)
                    if execution.execution_id in verified_ids:
                        result[key]["verified_ids"].add(execution.execution_id)
                    if execution.execution_id in rollback_failures:
                        result[key]["rollback_failure_ids"].add(execution.execution_id)
            return result

    def update_policy(self, policy_id: str, *, updates: dict, version: int):
        """
        يحدّث انتقالًا أو إعدادًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousRemediationPolicyModel).where(AutonomousRemediationPolicyModel.policy_id == policy_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous policy not found.")
            for key, value in updates.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            model.version = version
            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def set_policy_status(self, policy_id: str, status: str):
        """
        يحدّث انتقالًا أو إعدادًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها دون فقدان السجل السابق المرتبط به.
        """
        return self.update_policy(policy_id, updates={"status": status}, version=self.get_policy(policy_id).version)

    def resume_policy(self, policy_id: str):
        """
        يستأنف سياسة موقوفة ويبدأ لها دورة تشغيل جديدة بعد قرار مشغل صريح.
        """
        now = utc_now()
        with self._session_factory() as session:
            policy = session.scalar(
                select(AutonomousRemediationPolicyModel)
                .where(AutonomousRemediationPolicyModel.policy_id == policy_id)
                .with_for_update()
            )
            if policy is None:
                raise ValueError("Autonomous policy not found.")
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
                .with_for_update()
            )
            if runtime is None:
                runtime = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(runtime)
                session.flush()
            policy.status = AutonomousPolicyStatus.ENABLED.value
            policy.updated_at = now
            runtime.last_execution_at = None
            runtime.consecutive_failures = 0
            runtime.suspended_at = None
            runtime.suspension_reason = None
            runtime.triggering_execution_id = None
            runtime.triggering_decision_id = None
            runtime.updated_at = now
            session.commit()
            session.refresh(policy)
            return policy

    def record_autonomous_success(self, *, policy_id: str, policy_version: int | None = None, now=None):
        """
        يسجل حدثًا أو نتيجة جديدة في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء أثرها قابلًا للمراجعة.
        """
        now = now or utc_now()
        with self._session_factory() as session:
            policy = session.scalar(
                select(AutonomousRemediationPolicyModel)
                .where(AutonomousRemediationPolicyModel.policy_id == policy_id)
                .with_for_update()
            )
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
                .with_for_update()
            )
            if runtime is None:
                runtime = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(runtime)
                session.flush()
            if policy is None or policy_version is None or policy.version == policy_version:
                runtime.last_execution_at = now
                runtime.consecutive_failures = 0
                runtime.triggering_execution_id = None
                runtime.triggering_decision_id = None
                runtime.updated_at = now
            session.commit()
            session.refresh(runtime)
            return runtime
