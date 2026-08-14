from __future__ import annotations

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
    principal = getattr(request.state, "admin_user", None)
    return principal.username if principal is not None else fallback


@router.get("")
def list_remediation_plans(
    limit: int = Query(default=100, ge=1, le=500),
    status: str | None = Query(default=None),
    service: RemediationService = Depends(get_remediation_service),
):
    return serialize_value(service.list_plans(limit=limit, status=status))


@router.get("/{plan_id}")
def get_remediation_plan(
    plan_id: str,
    service: RemediationService = Depends(get_remediation_service),
):
    plan = service.get_plan(plan_id.strip())
    if plan is None:
        raise HTTPException(status_code=404, detail="Remediation plan not found.")
    return {
        "plan": serialize_value(plan),
        "approval": serialize_value(service.get_approval(plan_id=plan_id)),
        "execution": serialize_value(service.get_latest_execution(plan_id)),
        "sandbox_validation": serialize_value(service.get_sandbox_validation(plan_id=plan_id)),
    }


@router.get("/{plan_id}/audit")
def get_remediation_audit(
    plan_id: str,
    service: RemediationService = Depends(get_remediation_service),
):
    if service.get_plan(plan_id) is None:
        raise HTTPException(status_code=404, detail="Remediation plan not found.")
    return serialize_value(service.list_audit_events(plan_id))


@router.post("/{plan_id}/approval")
def request_remediation_approval(
    plan_id: str,
    payload: ApprovalRequest,
    service: RemediationService = Depends(get_remediation_service),
):
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
