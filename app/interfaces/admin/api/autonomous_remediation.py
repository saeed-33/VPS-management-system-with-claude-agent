from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.interfaces.admin.dependencies import (
    get_autonomous_candidate_service,
    get_autonomous_policy_service,
    get_autonomous_execution_service,
)
from app.interfaces.admin.schemas.autonomous_remediation import (
    AutonomousPolicyRequest,
    AutonomousPolicyUpdateRequest,
)
from app.interfaces.mcp.serializers import serialize_value


router = APIRouter(prefix="/api/autonomous-remediation", tags=["autonomous-remediation"])


def _actor(request: Request, fallback: str) -> str:
    principal = getattr(request.state, "admin_user", None)
    return principal.username if principal is not None else fallback


@router.post("/policies")
def create_policy(request: Request, payload: AutonomousPolicyRequest, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        values = payload.model_dump()
        values["created_by"] = _actor(request, values.get("created_by", "admin"))
        values["updated_by"] = values["created_by"]
        return serialize_value(service.create(**values))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/policies")
def list_policies(status: str | None = Query(default=None), service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    return serialize_value(service.list(status=status))


@router.get("/policies/{policy_id}")
def get_policy(policy_id: str, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    policy = service.get(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Autonomous policy not found.")
    return serialize_value(policy)


@router.patch("/policies/{policy_id}")
def update_policy(policy_id: str, request: Request, payload: AutonomousPolicyUpdateRequest, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        updates = payload.model_dump(exclude_none=True)
        updates["updated_by"] = _actor(request, updates.get("updated_by", "admin"))
        return serialize_value(service.update(policy_id, **updates))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/enable")
def enable_policy(policy_id: str, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.enable(policy_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/disable")
def disable_policy(policy_id: str, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.disable(policy_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/suspend")
def suspend_policy(policy_id: str, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.suspend(policy_id, reason="operator_suspension"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/resume")
def resume_policy(policy_id: str, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.resume(policy_id))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/candidates")
def list_candidates(service: AutonomousCandidateService = Depends(get_autonomous_candidate_service)):
    return serialize_value(service.list_candidates())


@router.get("/decisions")
def list_decisions(plan_id: str | None = Query(default=None), limit: int = Query(default=100), service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.list_decisions(plan_id=plan_id, limit=limit))


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str, service=Depends(get_autonomous_execution_service)):
    decision = service.get_decision(decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Autonomous decision not found.")
    return serialize_value(decision)


@router.get("/executions")
def list_executions(policy_id: str | None = Query(default=None), plan_id: str | None = Query(default=None), limit: int = Query(default=100), service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.list_reservations(policy_id=policy_id, plan_id=plan_id, limit=limit))


@router.get("/policies/{policy_id}/runtime")
def get_runtime_state(policy_id: str, service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.runtime_state(policy_id))


@router.get("/history")
def get_history(issue_fingerprint: str, action_type: str, target: str, service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.history(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target))
