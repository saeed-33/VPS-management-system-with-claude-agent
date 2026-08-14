from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.interfaces.admin.dependencies import (
    get_autonomous_candidate_service,
    get_autonomous_policy_service,
    get_autonomous_execution_service,
    get_remediation_service,
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
def enable_policy(policy_id: str, request: Request, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.enable(policy_id, actor=_actor(request, "admin")))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/disable")
def disable_policy(policy_id: str, request: Request, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.disable(policy_id, actor=_actor(request, "admin")))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/suspend")
def suspend_policy(policy_id: str, request: Request, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.suspend(policy_id, reason="operator_suspension", actor=_actor(request, "admin")))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/policies/{policy_id}/resume")
def resume_policy(policy_id: str, request: Request, service: AutonomousPolicyService = Depends(get_autonomous_policy_service)):
    try:
        return serialize_value(service.resume(policy_id, actor=_actor(request, "admin")))
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
    return [_reservation_view(item) for item in service.list_reservations(policy_id=policy_id, plan_id=plan_id, limit=limit)]


def _reservation_view(item) -> dict:
    return {
        "reservation_id": item.reservation_id,
        "idempotency_key": item.idempotency_key,
        "status": item.status,
        "policy_id": item.policy_id,
        "plan_id": item.plan_id,
        "plan_fingerprint": item.plan_fingerprint,
        "server_id": item.server_id,
        "action_type": item.action_type,
        "target": item.target,
        "authorization_id": item.authorization_id,
        "execution_id": item.execution_id,
        "created_at": getattr(item, "created_at", None),
        "expires_at": getattr(item, "expires_at", None),
        "completed_at": getattr(item, "completed_at", None),
    }


@router.get("/authorizations")
def list_authorizations(limit: int = Query(default=100), service=Depends(get_autonomous_execution_service)):
    return [
        {
            "authorization_id": item.authorization_id,
            "status": item.status,
            "policy_id": item.policy_id,
            "policy_version": item.policy_version,
            "decision_id": item.decision_id,
            "plan_id": item.plan_id,
            "plan_fingerprint": item.plan_fingerprint,
            "server_id": item.server_id,
            "action_type": item.action_type,
            "target": item.target,
            "sandbox_validation_id": item.sandbox_validation_id,
            "issued_at": item.issued_at,
            "expires_at": item.expires_at,
            "consumed_at": item.consumed_at,
        }
        for item in service.list_authorizations(limit=limit)
    ]


@router.get("/audit")
def list_autonomous_audit(
    policy_id: str | None = Query(default=None),
    plan_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    limit: int = Query(default=100),
    execution_service=Depends(get_autonomous_execution_service),
    remediation_service=Depends(get_remediation_service),
):
    policy_events = [
        {
            "source": "policy",
            "event_id": item.event_id,
            "policy_id": item.policy_id,
            "policy_version": item.policy_version,
            "event_type": item.event_type,
            "actor": item.actor,
            "payload": item.payload,
            "created_at": item.created_at,
        }
        for item in execution_service.list_policy_audit_events(policy_id=policy_id, limit=limit)
        if event_type is None or item.event_type == event_type
    ]
    plan_events = [
        {
            "source": "remediation",
            "event_id": item.event_id,
            "plan_id": item.plan_id,
            "event_type": item.event_type,
            "actor": item.actor,
            "server_id": item.server_id,
            "payload": item.payload,
            "created_at": item.created_at,
        }
        for item in remediation_service.list_all_audit_events(
            plan_id=plan_id, event_type=event_type, limit=limit
        )
        if item.event_type.startswith("autonomous_") or item.event_type in {
            "execution_started", "execution_succeeded", "execution_failed",
            "approval_requested", "approval_granted", "approval_rejected",
            "sandbox_validation_started", "sandbox_validation_passed",
            "sandbox_validation_failed", "sandbox_validation_stale",
        }
    ]
    return sorted(policy_events + plan_events, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:limit]


@router.get("/policies/{policy_id}/runtime")
def get_runtime_state(policy_id: str, service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.runtime_state(policy_id))


@router.get("/history")
def get_history(issue_fingerprint: str, action_type: str, target: str, service=Depends(get_autonomous_execution_service)):
    return serialize_value(service.history(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target))
