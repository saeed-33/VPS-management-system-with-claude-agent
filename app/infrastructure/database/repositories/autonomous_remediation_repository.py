"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.core.utils.datetime، app.infrastructure.database.models.remediation، app.infrastructure.database.session.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError

from app.core.contracts.autonomous_remediation import (
    AutonomousAuthorization,
    AutonomousAuthorizationStatus,
    AutonomousHistorySnapshot,
    AutonomousPolicyDecision,
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation import (
    AutonomousAuthorizationModel,
    AutonomousPolicyDecisionModel,
    AutonomousPolicyExecutionReservationModel,
    AutonomousPolicyRuntimeStateModel,
    AutonomousPolicyAuditEventModel,
    AutonomousRemediationPolicyModel,
    RemediationEvidenceModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    RemediationRollbackModel,
    RemediationVerificationModel,
)
from app.infrastructure.database.session import SessionLocal


class AutonomousRemediationRepository:
    """
    يمثل AutonomousRemediationRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, session_factory=SessionLocal) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def create_policy(self, policy: AutonomousRemediationPolicy):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create_policy؛ المدخلات المهمة: policy.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = self._policy_model(policy)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_policy(self, policy_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_policy؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousRemediationPolicyModel).where(AutonomousRemediationPolicyModel.policy_id == policy_id))

    def list_policies(self, *, status: str | None = None):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_policies؛ المدخلات المهمة: status.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousRemediationPolicyModel).order_by(AutonomousRemediationPolicyModel.created_at.desc())
            if status:
                statement = statement.where(AutonomousRemediationPolicyModel.status == status)
            return list(session.scalars(statement).all())

    def matching_policies(self, *, issue_fingerprint: str, action_type: str, target: str, server_id: int | None):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى matching_policies؛ المدخلات المهمة: issue_fingerprint، action_type، target، server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى candidate_keys؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_policy؛ المدخلات المهمة: policy_id، updates، version.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى set_policy_status؛ المدخلات المهمة: policy_id، status.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self.update_policy(policy_id, updates={"status": status}, version=self.get_policy(policy_id).version)

    def resume_policy(self, policy_id: str):
        """Enable a policy and atomically start a clean failure-count epoch."""
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
        """Persist a successful terminal outcome without a read/modify/write race."""
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

    def record_autonomous_failure(
        self, *, policy_id: str, policy_version: int | None, failure_key: str,
        decision_id: str | None, execution_id: str | None = None, now=None,
    ):
        """Atomically count one terminal failure and trip the policy breaker.

        ``failure_key`` is the durable reservation id when no execution row
        exists, otherwise the execution id.  It makes recovery and concurrent
        finalization idempotent without holding a transaction over SSH.
        """
        if not failure_key:
            raise ValueError("failure_key must not be empty.")
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
            if runtime.triggering_execution_id == failure_key and runtime.consecutive_failures > 0:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, False
            if policy is None or policy.version != policy_version:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, True
            if policy.status == AutonomousPolicyStatus.SUSPENDED.value:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, False

            # ``with_for_update`` is a no-op on SQLite.  The conditional
            # UPDATE is the actual compare-and-set guard, so a concurrent
            # finalizer with the same failure key can never increment twice.
            changed = session.execute(
                update(AutonomousPolicyRuntimeStateModel)
                .where(
                    AutonomousPolicyRuntimeStateModel.id == runtime.id,
                    or_(
                        AutonomousPolicyRuntimeStateModel.triggering_execution_id.is_(None),
                        AutonomousPolicyRuntimeStateModel.triggering_execution_id != failure_key,
                    ),
                )
                .values(
                    last_execution_at=now,
                    consecutive_failures=AutonomousPolicyRuntimeStateModel.consecutive_failures + 1,
                    triggering_execution_id=failure_key,
                    triggering_decision_id=decision_id,
                    updated_at=now,
                )
            )
            if changed.rowcount != 1:
                session.commit()
                current = session.scalar(
                    select(AutonomousPolicyRuntimeStateModel)
                    .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
                )
                return current or runtime, False, False, False
            session.flush()
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
            )
            threshold = max(1, int(policy.max_consecutive_failures or 1))
            trip = bool(
                policy.auto_suspend_on_failure
                and runtime.consecutive_failures >= threshold
                and policy.status == AutonomousPolicyStatus.ENABLED.value
            )
            if trip:
                policy.status = AutonomousPolicyStatus.SUSPENDED.value
                policy.updated_at = now
                runtime.suspended_at = now
                runtime.suspension_reason = "consecutive_failure_threshold"
                # Store the compare-and-set key, which is the execution id for
                # normal terminal failures and the reservation id for a
                # failure without an execution row.
                runtime.triggering_execution_id = failure_key
            session.commit()
            session.refresh(runtime)
            session.refresh(policy)
            return runtime, True, trip, False

    def create_decision(self, decision: AutonomousPolicyDecision, *, history: dict, metadata: dict | None = None):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create_decision؛ المدخلات المهمة: decision، history، metadata.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = AutonomousPolicyDecisionModel(
            decision_id=decision.decision_id, policy_id=decision.policy_id,
            policy_version=decision.policy_version, plan_id=decision.plan_id or "",
            plan_fingerprint=decision.plan_fingerprint or "", issue_fingerprint=decision.issue_fingerprint or "",
            server_id=decision.server_id, action_type=decision.action_type or "", target=decision.target or "",
            outcome=decision.outcome.value, reason_codes=list(decision.reason_codes),
            human_readable_reasons=list(decision.human_readable_reasons), history_snapshot=history,
            evaluation_metadata=metadata or decision.metadata,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_decisions؛ المدخلات المهمة: plan_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousPolicyDecisionModel).order_by(AutonomousPolicyDecisionModel.created_at.desc()).limit(limit)
            if plan_id:
                statement = statement.where(AutonomousPolicyDecisionModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def get_decision(self, decision_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_decision؛ المدخلات المهمة: decision_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousPolicyDecisionModel).where(AutonomousPolicyDecisionModel.decision_id == decision_id))

    def create_authorization(self, authorization: AutonomousAuthorization):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create_authorization؛ المدخلات المهمة: authorization.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = AutonomousAuthorizationModel(
            authorization_id=authorization.authorization_id, token=authorization.token,
            status=authorization.status.value, policy_id=authorization.policy_id,
            policy_version=authorization.policy_version, decision_id=authorization.decision_id,
            plan_id=authorization.plan_id, plan_fingerprint=authorization.plan_fingerprint,
            server_id=authorization.server_id, action_type=authorization.action_type,
            target=authorization.target, sandbox_validation_id=authorization.sandbox_validation_id,
            issued_at=authorization.issued_at, expires_at=authorization.expires_at,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def consume_authorization(self, authorization_id: str, *, now: datetime):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى consume_authorization؛ المدخلات المهمة: authorization_id، now.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousAuthorizationModel).where(AutonomousAuthorizationModel.authorization_id == authorization_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous authorization not found.")
            if model.status != AutonomousAuthorizationStatus.VALID.value:
                raise ValueError("Autonomous authorization is not valid.")
            expires_at = model.expires_at
            if expires_at.tzinfo is None and now.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=now.tzinfo)
            if expires_at <= now:
                model.status = AutonomousAuthorizationStatus.EXPIRED.value
                session.commit()
                raise ValueError("Autonomous authorization has expired.")
            model.status = AutonomousAuthorizationStatus.CONSUMED.value
            model.consumed_at = now
            session.commit()
            session.refresh(model)
            return model

    def get_authorization(self, authorization_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_authorization؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousAuthorizationModel).where(AutonomousAuthorizationModel.authorization_id == authorization_id))

    def list_authorizations(self, *, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_authorizations؛ المدخلات المهمة: limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(AutonomousAuthorizationModel)
                .order_by(AutonomousAuthorizationModel.issued_at.desc())
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def reserve(self, *, idempotency_key: str, owner_token: str, policy_id: str, plan_id: str, plan_fingerprint: str, action_type: str, target: str, server_id: int, now: datetime, lease_seconds: int = 900):
        """
        يدير reservation/finalization مع مراعاة idempotency وconcurrency ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى reserve؛ المدخلات المهمة: idempotency_key، owner_token، policy_id، plan_id، plan_fingerprint، action_type.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            # Lock the persisted plan when it exists.  This gives different
            # idempotency keys a shared database row to serialize on, while
            # the unique idempotency-key constraint remains the fallback for
            # callers that reserve before a plan row is present in a fixture.
            session.scalar(
                select(RemediationPlanModel)
                .where(RemediationPlanModel.plan_id == plan_id)
                .with_for_update()
            )
            existing = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key).with_for_update())
            binding = (policy_id, plan_id, plan_fingerprint, action_type, target, server_id)
            if existing is not None and (existing.policy_id, existing.plan_id, existing.plan_fingerprint, existing.action_type, existing.target, existing.server_id) != binding:
                raise ValueError("Idempotency key is bound to a different autonomous operation.")
            existing_expires_at = self._aware(existing.expires_at, now) if existing is not None else None
            if existing is not None and existing.status not in {"reserved", "in_progress"}:
                if existing.status == "expired":
                    recovered = self._claim_stale_reservation(
                        session=session, reservation=existing, owner_token=owner_token,
                        now=now, lease_seconds=lease_seconds,
                    )
                    session.commit()
                    if isinstance(recovered, AutonomousPolicyExecutionReservationModel):
                        session.refresh(recovered)
                    return recovered or existing
                return existing
            if existing is not None and existing_expires_at is not None and existing_expires_at > now:
                if existing.owner_token != owner_token:
                    return self._in_progress_view(existing)
                return existing
            active = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(
                AutonomousPolicyExecutionReservationModel.plan_id == plan_id,
                AutonomousPolicyExecutionReservationModel.status.in_(("reserved", "in_progress")),
            ).with_for_update())
            active_expires_at = self._aware(active.expires_at, now) if active is not None else None
            if active is not None and (active_expires_at is None or active_expires_at > now):
                if active.owner_token != owner_token:
                    return self._in_progress_view(active)
                return active
            if existing is not None and existing.status in {"reserved", "in_progress"}:
                recovered = self._claim_stale_reservation(
                    session=session, reservation=existing, owner_token=owner_token,
                    now=now, lease_seconds=lease_seconds,
                )
                session.commit()
                if isinstance(recovered, AutonomousPolicyExecutionReservationModel):
                    session.refresh(recovered)
                return recovered or existing
            if active is not None:
                if active.idempotency_key != idempotency_key:
                    return self._in_progress_view(active)
                recovered = self._claim_stale_reservation(
                    session=session, reservation=active, owner_token=owner_token,
                    now=now, lease_seconds=lease_seconds,
                )
                session.commit()
                if isinstance(recovered, AutonomousPolicyExecutionReservationModel):
                    session.refresh(recovered)
                return recovered or active

            # A completed/failed reservation for the same immutable plan
            # operation blocks a second idempotency key as well.  An explicit
            # operator resume clears ``last_execution_at`` and starts a new
            # runtime epoch, which is the only condition that permits a new
            # reservation for the same immutable plan.
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
            )
            new_runtime_epoch = bool(
                runtime is not None
                and runtime.last_execution_at is None
                and int(runtime.consecutive_failures or 0) == 0
                and runtime.triggering_execution_id is None
            )
            terminal = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(
                AutonomousPolicyExecutionReservationModel.plan_id == plan_id,
                AutonomousPolicyExecutionReservationModel.plan_fingerprint == plan_fingerprint,
                AutonomousPolicyExecutionReservationModel.server_id == server_id,
                AutonomousPolicyExecutionReservationModel.action_type == action_type,
                AutonomousPolicyExecutionReservationModel.target == target,
                AutonomousPolicyExecutionReservationModel.status.in_(("completed", "failed")),
            ).order_by(AutonomousPolicyExecutionReservationModel.completed_at.desc()))
            if terminal is not None and not new_runtime_epoch:
                return terminal

            model = AutonomousPolicyExecutionReservationModel(
                reservation_id=str(uuid4()), idempotency_key=idempotency_key, owner_token=owner_token, policy_id=policy_id,
                plan_id=plan_id, plan_fingerprint=plan_fingerprint, action_type=action_type,
                target=target, server_id=server_id, status="reserved", created_at=now,
                expires_at=now + timedelta(seconds=max(1, lease_seconds)),
            )
            session.add(model)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                winner = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key))
                winner_expires_at = self._aware(winner.expires_at, now) if winner is not None else None
                if (
                    winner is not None
                    and winner.owner_token != owner_token
                    and winner.status in {"reserved", "in_progress"}
                    and (winner_expires_at is None or winner_expires_at > now)
                ):
                    return self._in_progress_view(winner)
                return winner
            session.refresh(model)
            return model

    @staticmethod
    def _in_progress_view(reservation):
        """Return an observer view without mutating another owner's row."""
        return SimpleNamespace(
            reservation_id=reservation.reservation_id,
            idempotency_key=reservation.idempotency_key,
            owner_token=reservation.owner_token,
            policy_id=reservation.policy_id,
            plan_id=reservation.plan_id,
            plan_fingerprint=reservation.plan_fingerprint,
            action_type=reservation.action_type,
            target=reservation.target,
            server_id=reservation.server_id,
            status="in_progress",
            authorization_id=reservation.authorization_id,
            execution_id=reservation.execution_id,
            created_at=reservation.created_at,
            expires_at=reservation.expires_at,
            completed_at=reservation.completed_at,
        )

    def _claim_stale_reservation(self, *, session, reservation, owner_token: str, now: datetime, lease_seconds: int):
        """Atomically claim an expired lease before reconciling durable work."""
        claimed = session.execute(
            update(AutonomousPolicyExecutionReservationModel)
            .execution_options(synchronize_session=False)
            .where(
                AutonomousPolicyExecutionReservationModel.reservation_id == reservation.reservation_id,
                AutonomousPolicyExecutionReservationModel.status.in_(("reserved", "in_progress", "expired")),
                or_(
                    AutonomousPolicyExecutionReservationModel.status == "expired",
                    AutonomousPolicyExecutionReservationModel.expires_at <= now,
                ),
            )
            .values(
                owner_token=owner_token,
                expires_at=now + timedelta(seconds=max(1, lease_seconds)),
                completed_at=None,
            )
        )
        if claimed.rowcount != 1:
            current = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(
                AutonomousPolicyExecutionReservationModel.reservation_id == reservation.reservation_id,
            ))
            if current is not None and current.status in {"reserved", "in_progress"}:
                return self._in_progress_view(current)
            return current
        claimed_row = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(
            AutonomousPolicyExecutionReservationModel.reservation_id == reservation.reservation_id,
        ).with_for_update())
        return self._recover_stale_reservation(
            session=session, reservation=claimed_row, owner_token=owner_token,
            now=now, lease_seconds=lease_seconds,
        )

    @staticmethod
    def _execution_for_reservation(*, session, reservation):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى _execution_for_reservation؛ المدخلات المهمة: session، reservation.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        execution = session.scalar(select(RemediationExecutionModel).where(
            RemediationExecutionModel.idempotency_key == reservation.idempotency_key,
            RemediationExecutionModel.plan_id == reservation.plan_id,
            RemediationExecutionModel.server_id == reservation.server_id,
        ))
        if execution is None:
            return None
        plan = session.scalar(select(RemediationPlanModel).where(
            RemediationPlanModel.plan_id == reservation.plan_id,
        ))
        if plan is None or plan.plan_fingerprint != reservation.plan_fingerprint:
            return None
        action_ids = {
            str(item.get("id") or item.get("action_id") or "")
            for item in (plan.proposed_actions or [])
            if str(item.get("action_type") or item.get("type") or item.get("tool") or "") == reservation.action_type
            and str(item.get("target") or item.get("service") or "") == reservation.target
        }
        action_ids.add(reservation.action_type)
        return execution if execution.action_id in action_ids else None

    def _recover_stale_reservation(self, *, session, reservation, owner_token: str, now: datetime, lease_seconds: int):
        """Reconcile durable work before allowing a stale lease takeover."""
        execution = self._execution_for_reservation(session=session, reservation=reservation)
        if execution is not None:
            if execution.status == "succeeded":
                reservation.status = "completed"
                reservation.execution_id = execution.execution_id
                reservation.completed_at = now
                return reservation
            if execution.status in {"failed", "blocked"}:
                reservation.status = "failed"
                reservation.execution_id = execution.execution_id
                reservation.completed_at = now
                return reservation
            # An execution row exists but is not terminal.  Do not hand the
            # operation to another worker while its write may still be live.
            return self._in_progress_view(reservation)

        authorization = None
        if reservation.authorization_id:
            authorization = session.scalar(select(AutonomousAuthorizationModel).where(
                AutonomousAuthorizationModel.authorization_id == reservation.authorization_id,
            ))
        if authorization is not None and authorization.status == AutonomousAuthorizationStatus.CONSUMED.value:
            # A consumed authorization without a discoverable execution is an
            # uncertain crash boundary.  Close it as failed; never issue a new
            # authorization and guess that the write did not happen.
            reservation.status = "failed"
            reservation.completed_at = now
            return reservation
        if authorization is not None and authorization.status == AutonomousAuthorizationStatus.EXPIRED.value:
            reservation.authorization_id = None

        reservation.status = "reserved"
        reservation.owner_token = owner_token
        reservation.expires_at = now + timedelta(seconds=max(1, lease_seconds))
        reservation.completed_at = None
        reservation.execution_id = None
        return reservation

    def finalize_reservation(self, reservation_id: str, *, owner_token: str, status: str, execution_id: str | None = None):
        """
        يدير reservation/finalization مع مراعاة idempotency وconcurrency ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى finalize_reservation؛ المدخلات المهمة: reservation_id، owner_token، status، execution_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            if model.status not in {"reserved", "in_progress"}:
                raise ValueError("Autonomous reservation is not active.")
            model.status = status
            model.execution_id = execution_id
            model.completed_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def update_reservation_authorization(self, reservation_id: str, *, owner_token: str, authorization_id: str):
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_reservation_authorization؛ المدخلات المهمة: reservation_id، owner_token، authorization_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            if model.status not in {"reserved", "in_progress"}:
                raise ValueError("Autonomous reservation is not active.")
            if model.authorization_id is not None and model.authorization_id != authorization_id:
                raise ValueError("Autonomous reservation already has an authorization.")
            model.authorization_id = authorization_id
            session.commit()
            session.refresh(model)
            return model

    def get_runtime_state(self, policy_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_runtime_state؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyRuntimeStateModel).where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id))
            if model is None:
                model = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(model)
                session.commit()
                session.refresh(model)
            return model

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_reservations؛ المدخلات المهمة: policy_id، plan_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousPolicyExecutionReservationModel).order_by(AutonomousPolicyExecutionReservationModel.created_at.desc()).limit(limit)
            if policy_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.policy_id == policy_id)
            if plan_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def get_reservation_by_idempotency_key(self, idempotency_key: str):
        """Return the terminal or active reservation bound to an idempotency key."""
        with self._session_factory() as session:
            return session.scalar(
                select(AutonomousPolicyExecutionReservationModel).where(
                    AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key
                )
            )

    def update_runtime_state(self, policy_id: str, **updates):
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_runtime_state؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyRuntimeStateModel).where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id).with_for_update())
            if model is None:
                model = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(model)
                session.flush()
            for key, value in updates.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def append_policy_audit_event(self, *, policy_id: str, policy_version: int, event_type: str,
                                  actor: str = "admin", payload: dict | None = None):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى append_policy_audit_event؛ المدخلات المهمة: policy_id، policy_version، event_type، actor، payload.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = AutonomousPolicyAuditEventModel(
            event_id=str(uuid4()), policy_id=policy_id, policy_version=policy_version,
            event_type=event_type, actor=actor, payload=dict(payload or {}),
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_policy_audit_events(self, policy_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_policy_audit_events؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return list(session.scalars(
                select(AutonomousPolicyAuditEventModel)
                .where(AutonomousPolicyAuditEventModel.policy_id == policy_id)
                .order_by(AutonomousPolicyAuditEventModel.created_at.asc(), AutonomousPolicyAuditEventModel.id.asc())
            ).all())

    def list_all_policy_audit_events(self, *, policy_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_all_policy_audit_events؛ المدخلات المهمة: policy_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(AutonomousPolicyAuditEventModel)
                .order_by(AutonomousPolicyAuditEventModel.created_at.desc())
                .limit(limit)
            )
            if policy_id:
                statement = statement.where(
                    AutonomousPolicyAuditEventModel.policy_id == policy_id
                )
            return list(session.scalars(statement).all())

    def history(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى history؛ المدخلات المهمة: issue_fingerprint، action_type، target.
        تعيد AutonomousHistorySnapshot أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            plans = list(session.scalars(select(RemediationPlanModel)).all())
            plan_ids = {
                plan.plan_id for plan in plans
                if (
                    isinstance((plan.plan_metadata or {}).get("issue_fingerprint"), str)
                    and (plan.plan_metadata or {}).get("issue_fingerprint").strip()
                    and (plan.plan_metadata or {}).get("issue_fingerprint") == issue_fingerprint
                )
            }
            executions = list(session.scalars(select(RemediationExecutionModel).where(RemediationExecutionModel.plan_id.in_(plan_ids))).all()) if plan_ids else []
            verified_ids = {item.execution_id for item in session.scalars(select(RemediationVerificationModel).where(RemediationVerificationModel.status == "verified", RemediationVerificationModel.execution_id.in_([e.execution_id for e in executions]))).all()} if executions else set()
            rollback_rows = list(session.scalars(select(RemediationRollbackModel).where(RemediationRollbackModel.execution_id.in_([e.execution_id for e in executions]))).all()) if executions else []
            eligible_plan_ids = {
                plan.plan_id for plan in plans
                if plan.plan_id in plan_ids and any(
                    str(action.get("action_type") or action.get("type") or action.get("tool") or "") == action_type
                    and str(action.get("target") or action.get("service") or "") == target
                    for action in (plan.proposed_actions or [])
                )
            }
            supervised = [item for item in executions if item.plan_id in eligible_plan_ids and not (item.execution_metadata or {}).get("autonomous")]
            successes = [item for item in supervised if item.status == "succeeded"]
            failures = [item for item in supervised if item.status == "failed"]
            rollback_required = [item for item in rollback_rows if item.status in {"succeeded", "failed"}]
            return AutonomousHistorySnapshot(
                issue_fingerprint=issue_fingerprint, action_type=action_type, target=target,
                supervised_execution_count=len(supervised), successful_execution_count=len(successes),
                failed_execution_count=len(failures), verified_success_count=len(set(item.execution_id for item in successes) & verified_ids),
                verification_failure_count=len(set(item.execution_id for item in successes) - verified_ids),
                rollback_required_count=len(rollback_required), rollback_success_count=sum(item.status == "succeeded" for item in rollback_required),
                rollback_failure_count=sum(item.status == "failed" for item in rollback_required),
                autonomous_execution_count=sum(bool((item.execution_metadata or {}).get("autonomous")) for item in executions),
                autonomous_success_count=sum(bool((item.execution_metadata or {}).get("autonomous")) and item.status == "succeeded" for item in executions),
                autonomous_failure_count=sum(bool((item.execution_metadata or {}).get("autonomous")) and item.status != "succeeded" for item in executions),
                last_success_at=max((item.completed_at for item in successes if item.completed_at), default=None),
                last_failure_at=max((item.completed_at for item in failures if item.completed_at), default=None),
            )

    def execution_counts(self, *, policy_id: str, now: datetime):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى execution_counts؛ المدخلات المهمة: policy_id، now.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        from datetime import timedelta
        with self._session_factory() as session:
            rows = list(session.scalars(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.policy_id == policy_id)).all())
            return {
                "hour": sum(item.created_at >= now - timedelta(hours=1) for item in rows),
                "day": sum(item.created_at >= now - timedelta(days=1) for item in rows),
                "last": max((item.created_at for item in rows), default=None),
            }

    @staticmethod
    def _aware(value, reference: datetime):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى _aware؛ المدخلات المهمة: value، reference.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if value is None:
            return None
        if value.tzinfo is None and reference.tzinfo is not None:
            return value.replace(tzinfo=reference.tzinfo)
        return value

    @staticmethod
    def _policy_model(policy: AutonomousRemediationPolicy):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى _policy_model؛ المدخلات المهمة: policy.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return AutonomousRemediationPolicyModel(
            policy_id=policy.policy_id, name=policy.name, description=policy.description,
            status=policy.status.value, version=policy.version, issue_fingerprint=policy.issue_fingerprint,
            allowed_action_type=policy.allowed_action_type, allowed_target_pattern=policy.allowed_target_pattern,
            maximum_risk=policy.maximum_risk, minimum_confidence=policy.minimum_confidence,
            required_evidence=list(policy.required_evidence), minimum_success_count=policy.minimum_success_count,
            maximum_failure_rate=policy.maximum_failure_rate, maximum_rollback_failure_rate=policy.maximum_rollback_failure_rate,
            allowed_server_ids=list(policy.allowed_server_ids), allowed_server_tags=list(policy.allowed_server_tags),
            sandbox_required=policy.sandbox_required, sandbox_max_age_seconds=policy.sandbox_max_age_seconds,
            rollback_required=policy.rollback_required, cooldown_seconds=policy.cooldown_seconds,
            max_executions_per_hour=policy.max_executions_per_hour, max_executions_per_day=policy.max_executions_per_day,
            max_consecutive_failures=policy.max_consecutive_failures, auto_suspend_on_failure=policy.auto_suspend_on_failure,
            created_by=policy.created_by, updated_by=policy.updated_by,
        )
