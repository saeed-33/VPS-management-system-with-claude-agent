from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class RemediationPlanModel(Base):
    __tablename__ = "remediation_plans"
    __table_args__ = (
        Index(
            "ix_remediation_plans_investigation_created",
            "investigation_id",
            "created_at",
        ),
        Index(
            "ix_remediation_plans_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    investigation_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    server_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    problem_summary: Mapped[str] = mapped_column(
        String(4000),
        nullable=False,
    )
    proposed_actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    diagnosis_claim_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    plan_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    plan_fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    rollback_plan: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    sandbox_result_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    approval_requested_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    denial_reason: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    approval_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    approval_fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    approval_comment: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    approval_scope: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    approval_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    execution_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    verification_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    rollback_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    runtime_session_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    agent_job_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    plan_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class RemediationSandboxResultModel(Base):
    __tablename__ = "remediation_sandbox_results"
    __table_args__ = (
        Index(
            "ix_remediation_sandbox_plan_created",
            "plan_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    result_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    before_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    after_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    logs: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    result_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


class RemediationApprovalModel(Base):
    __tablename__ = "remediation_approvals"
    __table_args__ = (
        Index("ix_remediation_approvals_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_approvals_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    approval_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    approver: Mapped[str | None] = mapped_column(String(120), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    scope: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RemediationExecutionModel(Base):
    __tablename__ = "remediation_executions"
    __table_args__ = (
        Index("ix_remediation_executions_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_executions_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action_id: Mapped[str] = mapped_column(String(128), nullable=False)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    runtime_session_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    agent_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    exit_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str] = mapped_column(String(12000), nullable=False, default="")
    stderr: Mapped[str] = mapped_column(String(12000), nullable=False, default="")
    error: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)


class RemediationEvidenceModel(Base):
    __tablename__ = "remediation_evidence"
    __table_args__ = (
        Index("ix_remediation_evidence_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_evidence_execution_phase", "execution_id", "phase"),
        Index("ix_remediation_evidence_server_service", "server_id", "service"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    execution_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    phase: Mapped[str] = mapped_column(String(30), nullable=False)
    observed_state: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class SandboxValidationModel(Base):
    __tablename__ = "sandbox_validations"
    __table_args__ = (
        Index("ix_sandbox_validations_plan_created", "plan_id", "created_at"),
        Index("ix_sandbox_validations_plan_fingerprint", "plan_id", "plan_fingerprint"),
        Index("ix_sandbox_validations_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    validation_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="RESTRICT"), nullable=False, index=True)
    server_name: Mapped[str] = mapped_column(String(100), nullable=False)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    action_parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    expected_state: Mapped[str] = mapped_column(String(30), nullable=False)
    observed_state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    validation_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class RemediationVerificationModel(Base):
    __tablename__ = "remediation_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    verification_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    execution_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class RemediationRollbackModel(Base):
    __tablename__ = "remediation_rollbacks"
    id: Mapped[int] = mapped_column(primary_key=True)
    rollback_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    execution_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class RemediationAuditEventModel(Base):
    __tablename__ = "remediation_audit_events"
    __table_args__ = (
        Index("ix_remediation_audit_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_audit_event_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    server_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    runtime_session_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    agent_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class AutonomousRemediationPolicyModel(Base):
    __tablename__ = "autonomous_remediation_policies"
    __table_args__ = (
        Index("ix_autonomous_policies_match", "issue_fingerprint", "allowed_action_type", "status"),
        Index("ix_autonomous_policies_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    issue_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    allowed_action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    allowed_target_pattern: Mapped[str] = mapped_column(String(128), nullable=False)
    maximum_risk: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    minimum_confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)
    required_evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    minimum_success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_failure_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    maximum_rollback_failure_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    allowed_server_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    allowed_server_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sandbox_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sandbox_max_age_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)
    rollback_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_executions_per_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_executions_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    max_consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    auto_suspend_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class AutonomousPolicyDecisionModel(Base):
    __tablename__ = "autonomous_policy_decisions"
    __table_args__ = (
        Index("ix_autonomous_decisions_plan_created", "plan_id", "created_at"),
        Index("ix_autonomous_decisions_policy_created", "policy_id", "created_at"),
        Index("ix_autonomous_decisions_outcome", "outcome"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    policy_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    policy_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    issue_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    server_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    reason_codes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    human_readable_reasons: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    history_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evaluation_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class AutonomousAuthorizationModel(Base):
    __tablename__ = "autonomous_authorizations"
    __table_args__ = (
        Index("ix_autonomous_authorizations_plan", "plan_id", "status"),
        Index("ix_autonomous_authorizations_binding", "policy_id", "policy_version", "plan_fingerprint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    authorization_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(64), nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_id: Mapped[str] = mapped_column(String(64), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    sandbox_validation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AutonomousPolicyExecutionReservationModel(Base):
    __tablename__ = "autonomous_policy_execution_reservations"
    __table_args__ = (
        Index("ix_autonomous_reservations_plan", "plan_id", "created_at"),
        Index("ix_autonomous_reservations_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    owner_token: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    authorization_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    execution_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AutonomousPolicyRuntimeStateModel(Base):
    __tablename__ = "autonomous_policy_runtime_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    last_execution_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspension_reason: Mapped[str | None] = mapped_column(String(80), nullable=True)
    triggering_execution_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    triggering_decision_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class AutonomousPolicyAuditEventModel(Base):
    """Durable audit record for operator-level autonomous policy changes."""

    __tablename__ = "autonomous_policy_audit_events"
    __table_args__ = (
        Index("ix_autonomous_policy_audit_policy_created", "policy_id", "created_at"),
        Index("ix_autonomous_policy_audit_event_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False, default="admin")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
