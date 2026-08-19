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


class _ReservationOperationsMixin:
    """ينظم مجموعة من عمليات المستودع."""

    def reserve(self, *, idempotency_key: str, owner_token: str, policy_id: str, plan_id: str, plan_fingerprint: str, action_type: str, target: str, server_id: int, now: datetime, lease_seconds: int = 900):
        """
        يحجز سجلًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها لمنع تنفيذ متزامن أو تكرار الأثر نفسه.
        """
        with self._session_factory() as session:
            # نقفل الخطة المحفوظة إن وجدت حتى تتسلسل الطلبات المختلفة على نفس
            # التغيير، ويبقى القيد الفريد حارسًا عندما يسبق الحجز حفظ الخطة.
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

            # يمنع الحجز المكتمل أو الفاشل لخطة ثابتة مفتاحًا ثانيًا أيضًا؛ ولا
            # يسمح بمحاولة جديدة إلا بعد استئناف صريح يبدأ دورة تشغيل جديدة.
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
        """
        ينفذ تحققًا داخليًا لازمًا لحفظ أو قراءة سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها.
        """
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
        """
        يفحص حالة تنفيذ أو حجز داخل سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها قبل السماح بانتقاله التالي.
        """
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
        يفحص حالة تنفيذ أو حجز داخل سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها قبل السماح بانتقاله التالي.
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
        """
        يفحص حالة تنفيذ أو حجز داخل سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها قبل السماح بانتقاله التالي.
        """
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
            # يوجد تنفيذ لم يغلق بعد؛ لا نسلمه لعامل آخر بينما قد يكون التغيير
            # ما زال جاريًا على السيرفر.
            return self._in_progress_view(reservation)

        authorization = None
        if reservation.authorization_id:
            authorization = session.scalar(select(AutonomousAuthorizationModel).where(
                AutonomousAuthorizationModel.authorization_id == reservation.authorization_id,
            ))
        if authorization is not None and authorization.status == AutonomousAuthorizationStatus.CONSUMED.value:
            # الموافقة المستهلكة بلا تنفيذ معروف تعني نقطة فشل غير محسومة؛
            # نغلقها كفشل ولا نصدر موافقة جديدة بافتراض أن التغيير لم يحدث.
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
