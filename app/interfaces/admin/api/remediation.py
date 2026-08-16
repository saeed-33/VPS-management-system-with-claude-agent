"""
نقاط API لدورة معالجة المشكلة.

تسلسل المسارات عرض الخطط والموافقات والتدقيق، والتحقق المعزول، والموافقة
والرفض والتنفيذ والتراجع، مع تحويل نماذج المجال إلى JSON آمن للواجهة.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.capabilities.remediation.service import RemediationService
from app.interfaces.admin.dependencies import get_remediation_service
from app.interfaces.admin.schemas.remediation import (
    ApprovalDecisionRequest,
    ApprovalRequest,
    ExecuteRemediationRequest,
    RollbackRemediationRequest,
    SandboxValidationRequest,
)
from app.interfaces.mcp.serializers import serialize_value


router = APIRouter(prefix="/api/remediation", tags=["remediation"])


def _actor(request: Request, fallback: str | None) -> str | None:
    """
    يستخرج هوية الفاعل الإداري لتسجيل عمليات المعالجة.
    """
    principal = getattr(request.state, "admin_user", None)
    return principal.username if principal is not None else fallback


def _json_value(value: Any) -> Any:
    """
    يحوّل قيمة المجال إلى قيمة قابلة للتسلسل في JSON.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return str(value)


def _serialize_fields(value: Any, names: tuple[str, ...]) -> dict[str, Any] | None:
    """
    يحول حقول خطة المعالجة إلى قاموس استجابة منظم.
    """
    if value is None:
        return None
    return {name: _json_value(getattr(value, name, None)) for name in names}


_PLAN_FIELDS = (
    "id", "plan_id", "investigation_id", "server_id", "title", "problem_summary",
    "proposed_actions", "diagnosis_claim_ids", "evidence_ids", "risk_level",
    "plan_version", "plan_fingerprint", "rollback_plan", "status", "sandbox_result_id",
    "approval_requested_at", "approved_by", "approved_at", "denial_reason",
    "approval_status", "approval_fingerprint", "approval_comment", "approval_scope",
    "approval_expires_at", "execution_status", "verification_status", "rollback_status",
    "runtime_session_id", "agent_job_id", "plan_metadata", "created_at", "updated_at",
)
_APPROVAL_FIELDS = (
    "id", "approval_id", "plan_id", "plan_fingerprint", "status", "approver", "comment",
    "scope", "expires_at", "created_at", "decided_at",
)
_EXECUTION_FIELDS = (
    "id", "execution_id", "plan_id", "action_id", "server_id", "status", "actor",
    "runtime_session_id", "agent_job_id", "before_evidence_ids", "after_evidence_ids",
    "exit_status", "created_at", "started_at", "completed_at",
)
_SANDBOX_VALIDATION_FIELDS = (
    "id", "validation_id", "plan_id", "plan_fingerprint", "server_id", "server_name",
    "service", "action_type", "action_parameters", "expected_state", "observed_state",
    "before_evidence_ids", "after_evidence_ids", "verification_status", "status",
    "started_at", "finished_at", "failure_reason", "validation_metadata", "created_at",
)
_AUDIT_FIELDS = (
    "id", "event_id", "plan_id", "event_type", "actor", "server_id", "runtime_session_id",
    "agent_job_id", "payload", "created_at",
)


def _serialize_plan(value: Any) -> dict[str, Any] | None:
    """
    يحوّل خطة المعالجة إلى تمثيل API شامل.
    """
    return _serialize_fields(value, _PLAN_FIELDS)


def _serialize_approval(value: Any) -> dict[str, Any] | None:
    """
    يحوّل طلب الموافقة إلى تمثيل API.
    """
    return _serialize_fields(value, _APPROVAL_FIELDS)


def _serialize_execution(value: Any) -> dict[str, Any] | None:
    """
    يحوّل سجل التنفيذ إلى تمثيل آمن للواجهة.
    """
    return _serialize_fields(value, _EXECUTION_FIELDS)


def _serialize_sandbox_validation(value: Any) -> dict[str, Any] | None:
    """
    يحوّل نتيجة التحقق المعزول إلى تمثيل API.
    """
    return _serialize_fields(value, _SANDBOX_VALIDATION_FIELDS)


def _serialize_audit(value: Any) -> dict[str, Any] | None:
    """
    يحوّل حدث التدقيق إلى بيانات JSON قابلة للعرض.
    """
    return _serialize_fields(value, _AUDIT_FIELDS)


@router.get("")
def list_remediation_plans(
    limit: int = Query(default=100, ge=1, le=500),
    status: str | None = Query(default=None),
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يعرض خطط المعالجة مع مرشحات الحالة والسيرفر والتشخيص.
    """
    return [_serialize_plan(plan) for plan in service.list_plans(limit=limit, status=status)]


@router.get("/{plan_id}")
def get_remediation_plan(
    plan_id: str,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يعيد خطة معالجة محددة أو HTTP 404.
    """
    plan = service.get_plan(plan_id.strip())
    if plan is None:
        raise HTTPException(status_code=404, detail="Remediation plan not found.")
    return {
        "plan": _serialize_plan(plan),
        "approval": _serialize_approval(service.get_approval(plan_id=plan_id)),
        "execution": _serialize_execution(service.get_latest_execution(plan_id)),
        "sandbox_validation": _serialize_sandbox_validation(service.get_sandbox_validation(plan_id=plan_id)),
    }


@router.get("/{plan_id}/audit")
def get_remediation_audit(
    plan_id: str,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يعرض أحداث تدقيق خطة المعالجة.
    """
    if service.get_plan(plan_id) is None:
        raise HTTPException(status_code=404, detail="Remediation plan not found.")
    return [_serialize_audit(event) for event in service.list_audit_events(plan_id)]


@router.post("/{plan_id}/approval")
def request_remediation_approval(
    plan_id: str,
    payload: ApprovalRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    ينشئ طلب موافقة لخطة معالجة بعد التحقق من صلاحيتها.
    """
    try:
        return serialize_value(service.request_approval(plan_id=plan_id, expires_in_seconds=payload.expires_in_seconds, scope=payload.scope))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{plan_id}/sandbox-validation")
def validate_remediation_in_sandbox(
    plan_id: str,
    payload: SandboxValidationRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يشغل التحقق المعزول للخطة ويعيد نتيجة السلامة.
    """
    try:
        result = service.validate_in_isolated_sandbox(plan_id=plan_id, **payload.model_dump())
        return serialize_value(result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{plan_id}/approval/{approval_id}/approve")
def approve_remediation(
    plan_id: str,
    approval_id: str,
    request: Request,
    payload: ApprovalDecisionRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يعتمد خطة المعالجة بعد تحقق الصلاحية والضوابط.
    """
    try:
        existing = service.get_approval(approval_id)
        if existing is None or existing.plan_id != plan_id:
            raise ValueError("Approval does not belong to this plan.")
        approval = service.approve(approval_id=approval_id, approver=_actor(request, payload.approver), comment=payload.comment, scope=payload.scope)
        return serialize_value(approval)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{plan_id}/approval/{approval_id}/reject")
def reject_remediation(
    plan_id: str,
    approval_id: str,
    request: Request,
    payload: ApprovalDecisionRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يرفض طلب معالجة ويسجل سبب الرفض.
    """
    try:
        existing = service.get_approval(approval_id)
        if existing is None or existing.plan_id != plan_id:
            raise ValueError("Approval does not belong to this plan.")
        approval = service.reject(approval_id=approval_id, approver=_actor(request, payload.approver), comment=payload.comment)
        return serialize_value(approval)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{plan_id}/execute")
def execute_remediation(
    plan_id: str,
    request: Request,
    payload: ExecuteRemediationRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    ينفذ خطة معالجة معتمدة ويعيد سجل النتيجة.
    """
    try:
        values = payload.model_dump()
        values["actor"] = _actor(request, values["actor"])
        outcome = service.apply_approved(plan_id=plan_id, **values)
        if not outcome.get("applied"):
            raise HTTPException(status_code=409, detail=outcome)
        return serialize_value(outcome)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{plan_id}/rollback")
def rollback_remediation(
    plan_id: str,
    request: Request,
    payload: RollbackRemediationRequest,
    service: RemediationService = Depends(get_remediation_service),
):
    """
    يطلب أو ينفذ تراجع خطة المعالجة ويعيد نتيجته.
    """
    try:
        values = payload.model_dump()
        values["actor"] = _actor(request, values["actor"])
        outcome = service.rollback(plan_id=plan_id, **values)
        if not outcome.get("rolled_back"):
            raise HTTPException(status_code=409, detail=outcome)
        return serialize_value(outcome)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
