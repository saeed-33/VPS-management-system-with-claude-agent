from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
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
    AutonomousRemediationPolicyModel,
    RemediationEvidenceModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    RemediationRollbackModel,
    RemediationVerificationModel,
)
from app.infrastructure.database.session import SessionLocal


class AutonomousRemediationRepository:
    def __init__(self, session_factory=SessionLocal) -> None:
        self._session_factory = session_factory

    def create_policy(self, policy: AutonomousRemediationPolicy):
        model = self._policy_model(policy)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_policy(self, policy_id: str):
        with self._session_factory() as session:
            return session.scalar(select(AutonomousRemediationPolicyModel).where(AutonomousRemediationPolicyModel.policy_id == policy_id))

    def list_policies(self, *, status: str | None = None):
        with self._session_factory() as session:
            statement = select(AutonomousRemediationPolicyModel).order_by(AutonomousRemediationPolicyModel.created_at.desc())
            if status:
                statement = statement.where(AutonomousRemediationPolicyModel.status == status)
            return list(session.scalars(statement).all())

    def matching_policies(self, *, issue_fingerprint: str, action_type: str, target: str, server_id: int | None):
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
        return self.update_policy(policy_id, updates={"status": status}, version=self.get_policy(policy_id).version)

    def create_decision(self, decision: AutonomousPolicyDecision, *, history: dict, metadata: dict | None = None):
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
        with self._session_factory() as session:
            statement = select(AutonomousPolicyDecisionModel).order_by(AutonomousPolicyDecisionModel.created_at.desc()).limit(limit)
            if plan_id:
                statement = statement.where(AutonomousPolicyDecisionModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def get_decision(self, decision_id: str):
        with self._session_factory() as session:
            return session.scalar(select(AutonomousPolicyDecisionModel).where(AutonomousPolicyDecisionModel.decision_id == decision_id))

    def create_authorization(self, authorization: AutonomousAuthorization):
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
        with self._session_factory() as session:
            return session.scalar(select(AutonomousAuthorizationModel).where(AutonomousAuthorizationModel.authorization_id == authorization_id))

    def reserve(self, *, idempotency_key: str, owner_token: str, policy_id: str, plan_id: str, plan_fingerprint: str, action_type: str, target: str, server_id: int, now: datetime, lease_seconds: int = 900):
        with self._session_factory() as session:
            existing = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key).with_for_update())
            binding = (policy_id, plan_id, plan_fingerprint, action_type, target, server_id)
            if existing is not None and (existing.policy_id, existing.plan_id, existing.plan_fingerprint, existing.action_type, existing.target, existing.server_id) != binding:
                raise ValueError("Idempotency key is bound to a different autonomous operation.")
            existing_expires_at = self._aware(existing.expires_at, now) if existing is not None else None
            if existing is not None and existing.status not in {"reserved", "in_progress"}:
                return existing
            if existing is not None and existing_expires_at is not None and existing_expires_at > now:
                if existing.owner_token != owner_token:
                    existing.status = "in_progress"
                return existing
            if existing is not None and existing.status in {"reserved", "in_progress"}:
                existing.status = "expired"
                existing.completed_at = now
                session.flush()
            if existing is not None and existing.status == "expired":
                existing.status = "reserved"
                existing.owner_token = owner_token
                existing.expires_at = now + timedelta(seconds=max(1, lease_seconds))
                existing.completed_at = None
                existing.authorization_id = None
                existing.execution_id = None
                session.commit()
                session.refresh(existing)
                return existing
            active = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(
                AutonomousPolicyExecutionReservationModel.plan_id == plan_id,
                AutonomousPolicyExecutionReservationModel.status.in_(("reserved", "in_progress")),
            ).with_for_update())
            active_expires_at = self._aware(active.expires_at, now) if active is not None else None
            if active is not None and (active_expires_at is None or active_expires_at > now):
                if active.owner_token != owner_token:
                    active.status = "in_progress"
                return active
            if active is not None:
                active.status = "expired"
                active.completed_at = now
                session.flush()
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
                return session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key))
            session.refresh(model)
            return model

    def finalize_reservation(self, reservation_id: str, *, owner_token: str, status: str, execution_id: str | None = None):
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            model.status = status
            model.execution_id = execution_id
            model.completed_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def update_reservation_authorization(self, reservation_id: str, *, owner_token: str, authorization_id: str):
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            model.authorization_id = authorization_id
            session.commit()
            session.refresh(model)
            return model

    def get_runtime_state(self, policy_id: str):
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyRuntimeStateModel).where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id))
            if model is None:
                model = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(model)
                session.commit()
                session.refresh(model)
            return model

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        with self._session_factory() as session:
            statement = select(AutonomousPolicyExecutionReservationModel).order_by(AutonomousPolicyExecutionReservationModel.created_at.desc()).limit(limit)
            if policy_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.policy_id == policy_id)
            if plan_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def update_runtime_state(self, policy_id: str, **updates):
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

    def history(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
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
        if value is None:
            return None
        if value.tzinfo is None and reference.tzinfo is not None:
            return value.replace(tzinfo=reference.tzinfo)
        return value

    @staticmethod
    def _policy_model(policy: AutonomousRemediationPolicy):
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
