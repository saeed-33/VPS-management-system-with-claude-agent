"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.core.contracts.remediation، app.core.policies.autonomous_remediation، app.core.utils.datetime.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from sqlalchemy.exc import OperationalError
from uuid import uuid4

from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousPolicyStatus,
)
from app.core.contracts.remediation import RemediationAction
from app.core.contracts.remediation import RemediationPlanStatus
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator
from app.core.utils.datetime import utc_now


class AutonomousExecutionService:
    """Phase 7 coordinator; all writes remain in RemediationService."""

    def __init__(self, *, repository, remediation_repository, remediation_service, policy_service, history_service, candidate_service, authorization_service, evaluator=None, automatic_remediation_allowed=False):
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository، remediation_repository، remediation_service، policy_service، history_service، candidate_service.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository
        self._remediation_repository = remediation_repository
        self._remediation_service = remediation_service
        self._policy_service = policy_service
        self._history_service = history_service
        self._candidate_service = candidate_service
        self._authorization_service = authorization_service
        self._evaluator = evaluator or AutonomousRemediationPolicyEvaluator()
        self._automatic_remediation_allowed = automatic_remediation_allowed

    def evaluate(self, *, plan_id: str):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى evaluate؛ المدخلات المهمة: plan_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        plan = self._remediation_repository.get_plan(plan_id)
        if plan is None:
            raise ValueError("Remediation plan not found.")
        action = self._single_action(plan)
        now = utc_now()
        issue_fingerprint = str((plan.plan_metadata or {}).get("issue_fingerprint") or "")
        matches = self._repository.matching_policies(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target, server_id=plan.server_id)
        policy_model, ambiguous_policy_match = self._select_policy(matches)
        policy = self._policy_service._model_to_contract(policy_model) if policy_model is not None else None
        history = self._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target)
        counts = self._repository.execution_counts(policy_id=policy.policy_id, now=now) if policy else {"hour": 0, "day": 0, "last": None}
        runtime = self._repository.get_runtime_state(policy.policy_id) if policy else None
        sandbox = self._remediation_repository.get_latest_sandbox_validation(plan_id)
        reservations = self._repository.list_reservations(plan_id=plan_id, limit=1)
        sandbox_evidence_valid = self._remediation_repository.sandbox_evidence_belongs(
            validation=sandbox,
        ) if sandbox is not None else False
        context = AutonomousEvaluationContext(
            global_enabled=self._automatic_remediation_allowed, now=now, policy=policy,
            plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint or "", issue_fingerprint=issue_fingerprint,
            server_id=plan.server_id, action_type=action.action_type, target=action.target,
            risk=str(plan.risk_level), confidence=float((plan.plan_metadata or {}).get("confidence", 1.0)),
            diagnosis_evidence_valid=bool(plan.diagnosis_claim_ids), plan_evidence_valid=bool(plan.evidence_ids),
            sandbox=sandbox, history=history,
            last_execution_at=counts["last"], hourly_execution_count=counts["hour"], daily_execution_count=counts["day"],
            consecutive_failures=int(runtime.consecutive_failures if runtime else 0),
            execution_completed=False, execution_in_progress=bool(reservations and reservations[0].status in {"reserved", "in_progress"}),
            plan_ready=plan.status in {RemediationPlanStatus.SANDBOX_PASSED.value, RemediationPlanStatus.APPROVED.value},
            ambiguous_policy_match=ambiguous_policy_match,
            sandbox_evidence_valid=sandbox_evidence_valid,
            error_classification=(plan.plan_metadata or {}).get("error_classification"),
        )
        decision = self._evaluator.evaluate(context)
        self._repository.create_decision(decision, history=self._history_dict(history), metadata={"policy_status": policy.status.value if policy else None})
        self._audit(plan_id, "autonomous_policy_evaluated", {
            "decision_id": decision.decision_id, "outcome": decision.outcome.value,
            "reason_codes": list(decision.reason_codes), "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
        })
        return decision, plan, action, policy, sandbox, history

    @staticmethod
    def _select_policy(matches):
        """Select one policy deterministically after exact structural matching.

        Enabled policies are the only policies that can create autonomous
        ambiguity. Disabled and suspended policies remain selectable when no
        enabled policy exists so the evaluator can preserve their explicit
        deny semantics. Unknown statuses fail closed as ambiguity.
        """
        enabled = []
        inactive = []
        unknown = []
        for policy in matches:
            status = getattr(policy.status, "value", policy.status)
            if status == AutonomousPolicyStatus.ENABLED.value:
                enabled.append(policy)
            elif status in {
                AutonomousPolicyStatus.DISABLED.value,
                AutonomousPolicyStatus.SUSPENDED.value,
            }:
                inactive.append(policy)
            else:
                unknown.append(policy)

        if len(enabled) == 1:
            return enabled[0], False
        if len(enabled) > 1:
            return None, True
        if len(inactive) == 1 and not unknown:
            return inactive[0], False
        if not inactive and not unknown:
            return None, False
        return None, True

    def attempt(self, *, plan_id: str, actor: str = "autonomous-policy", idempotency_key: str | None = None):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى attempt؛ المدخلات المهمة: plan_id، actor، idempotency_key.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        plan = self._remediation_repository.get_plan(plan_id)
        if plan is None:
            raise ValueError("Remediation plan not found.")
        action = self._single_action(plan)

        existing = None
        if idempotency_key is not None:
            existing = self._repository.get_reservation_by_idempotency_key(idempotency_key)
            if existing is not None and not self._reservation_lease_stale(existing, now=utc_now()):
                return self._replay_existing_reservation(
                    existing=existing, plan=plan, action=action, idempotency_key=idempotency_key,
                )
        stale_existing = existing if existing is not None and self._reservation_lease_stale(existing, now=utc_now()) else None

        decision, plan, action, policy, sandbox, history = self.evaluate(plan_id=plan_id)
        if decision.outcome == AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL:
            if sandbox is None or sandbox.status != "passed":
                return {"outcome": decision.outcome.value, "decision": decision, "approval": None}
            approval = self._remediation_service.request_approval(plan_id=plan_id)
            return {"outcome": decision.outcome.value, "decision": decision, "approval": approval}
        if decision.outcome != AutonomousDecisionOutcome.AUTO_EXECUTE:
            return {"outcome": decision.outcome.value, "decision": decision}

        key = idempotency_key or f"autonomous:{policy.policy_id}:{plan.plan_id}:{plan.plan_fingerprint}:{action.action_type}:{action.target}"
        if stale_existing is None:
            candidate = self._repository.get_reservation_by_idempotency_key(key)
            if candidate is not None and self._reservation_lease_stale(candidate, now=utc_now()):
                stale_existing = candidate
        owner_token = str(uuid4())
        reservation = self._repository.reserve(
            idempotency_key=key, owner_token=owner_token, policy_id=policy.policy_id, plan_id=plan.plan_id,
            plan_fingerprint=plan.plan_fingerprint, action_type=action.action_type, target=action.target,
            server_id=plan.server_id, now=utc_now(),
        )
        if not self._reservation_matches(
            reservation=reservation, plan=plan, action=action, idempotency_key=key,
        ):
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_binding_mismatch",
                "reservation": self._reservation_view(reservation),
            }
        if stale_existing is not None:
            self._audit(plan_id, "autonomous_reservation_recovered", {
                "reservation_id": reservation.reservation_id,
                "idempotency_key": reservation.idempotency_key,
                "owner_token_replaced": reservation.owner_token == owner_token,
                "authorization_id": reservation.authorization_id,
                "execution_id": reservation.execution_id,
            })
        self._audit(plan_id, "autonomous_execution_reserved", {
            "reservation_id": reservation.reservation_id, "idempotency_key": reservation.idempotency_key,
            "policy_id": policy.policy_id, "decision_id": decision.decision_id,
        })
        if reservation.status == "completed":
            return self._replay_existing_reservation(
                existing=reservation, plan=plan, action=action, idempotency_key=key,
                decision=decision,
            )
        if reservation.status == "failed":
            if stale_existing is not None:
                runtime = self._record_runtime(
                    policy, decision, False, reservation.execution_id,
                    failure_key=reservation.execution_id or reservation.reservation_id,
                )
                self._audit(plan_id, "autonomous_execution_failed", {
                    "reservation_id": reservation.reservation_id,
                    "execution_id": reservation.execution_id,
                    "recovered": True,
                    "consecutive_failures": getattr(runtime, "consecutive_failures", None),
                })
            return {
                "outcome": "deny",
                "decision": decision,
                "error": "idempotency_reservation_not_replayable",
                "reservation": self._reservation_view(reservation),
            }
        if reservation.status != "reserved":
            return {
                "outcome": "in_progress", "idempotent": True,
                "decision": decision, "reservation": self._reservation_view(reservation),
            }

        try:
            authorization = None
            if reservation.authorization_id:
                loader = getattr(self._authorization_service, "get", None)
                if loader is None:
                    raise ValueError("authorization_stale:recovery_loader_missing")
                authorization = loader(reservation.authorization_id)
                if authorization.status != "valid":
                    raise ValueError("authorization_stale:recovery")
            else:
                authorization = self._authorization_service.issue(decision=decision, sandbox_validation_id=sandbox.validation_id)
                self._audit(plan_id, "autonomous_authorization_issued", {
                    "authorization_id": authorization.authorization_id, "decision_id": decision.decision_id,
                    "sandbox_validation_id": authorization.sandbox_validation_id,
                })
                self._repository.update_reservation_authorization(reservation.reservation_id, owner_token=owner_token, authorization_id=authorization.authorization_id)
            authorization = self._authorization_service.consume(authorization.authorization_id)
            self._audit(plan_id, "autonomous_authorization_consumed", {"authorization_id": authorization.authorization_id})
            current_plan = self._remediation_repository.get_plan(plan_id)
            current_policy_model = self._repository.get_policy(policy.policy_id)
            current_sandbox = self._remediation_repository.get_sandbox_validation(sandbox.validation_id)
            if current_plan is None or (
                authorization.policy_id != decision.policy_id
                or authorization.policy_version != decision.policy_version
                or authorization.decision_id != decision.decision_id
                or authorization.plan_id != current_plan.plan_id
                or authorization.plan_fingerprint != current_plan.plan_fingerprint
                or authorization.server_id != current_plan.server_id
                or authorization.action_type != action.action_type
                or authorization.target != action.target
            ):
                raise ValueError("authorization_stale:binding")
            if (
                current_policy_model is None
                or current_policy_model.policy_id != authorization.policy_id
                or current_policy_model.version != authorization.policy_version
                or current_policy_model.status != "enabled"
            ):
                raise ValueError("authorization_stale:policy_version")
            if current_sandbox is None or current_sandbox.plan_fingerprint != authorization.plan_fingerprint or current_sandbox.status != "passed":
                raise ValueError("authorization_stale:sandbox")
            if (current_sandbox.server_id, current_sandbox.action_type, current_sandbox.service) != (
                authorization.server_id, authorization.action_type, authorization.target
            ) or current_sandbox.validation_id != authorization.sandbox_validation_id:
                raise ValueError("authorization_stale:binding")
            # لا تكفي autonomous decision وحدها: نعيد فحص binding للـpolicy
            # والنسخة والـsandbox قبل أي write operation ثم نسجل النتيجة.
            outcome = self._remediation_service.apply_approved(
                plan_id=plan.plan_id, server_id=plan.server_id, actor=actor,
                idempotency_key=key, autonomous_authorization=authorization,
            )
            if not outcome.get("applied") and outcome.get("execution_id"):
                rollback = self._remediation_service.rollback(plan_id=plan.plan_id, execution_id=outcome["execution_id"], actor=actor, server_id=plan.server_id)
                outcome["autonomous_rollback"] = rollback
            success = bool(outcome.get("applied"))
            # reservation تمنع concurrent execution لنفس idempotency key؛
            # finalize تربط execution_id بسجل التدقيق وتحفظ success/failure.
            self._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="completed" if success else "failed", execution_id=outcome.get("execution_id"))
            self._record_runtime(
                policy, decision, success, outcome.get("execution_id"),
                failure_key=outcome.get("execution_id") or reservation.reservation_id,
            )
            self._audit(plan_id, "autonomous_execution_finalized", {
                "reservation_id": reservation.reservation_id, "execution_id": outcome.get("execution_id"),
                "success": success,
            })
            if not success:
                self._audit(plan_id, "autonomous_execution_failed", {
                    "reservation_id": reservation.reservation_id,
                    "execution_id": outcome.get("execution_id"),
                    "blocked_reason": outcome.get("blocked_reason"),
                    "rollback": outcome.get("autonomous_rollback"),
                })
            return {"outcome": "auto_execute", "decision": decision, "authorization_id": authorization.authorization_id, "result": outcome}
        except Exception as exc:
            self._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="failed")
            self._record_runtime(
                policy, decision, False, None,
                failure_key=reservation.reservation_id,
            )
            self._audit(plan_id, "autonomous_execution_failed", {
                "reservation_id": reservation.reservation_id, "error": str(exc),
            })
            return {"outcome": "deny", "decision": decision, "authorization_id": locals().get("authorization", None).authorization_id if locals().get("authorization") else None, "error": str(exc)}

    def _replay_existing_reservation(self, *, existing, plan, action, idempotency_key: str, decision=None):
        """Return an exact reservation replay without evaluation or re-execution."""
        if not self._reservation_matches(
            reservation=existing, plan=plan, action=action, idempotency_key=idempotency_key,
        ):
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_binding_mismatch",
                "reservation": self._reservation_view(existing),
            }
        if existing.status in {"reserved", "in_progress"}:
            return {
                "outcome": "in_progress",
                "idempotent": True,
                "reservation": self._reservation_view(existing),
            }
        if existing.status != "completed":
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_not_replayable",
                "reservation": self._reservation_view(existing),
            }
        if not existing.execution_id:
            return {
                "outcome": "deny",
                "error": "completed_reservation_missing_execution",
                "reservation": self._reservation_view(existing),
            }
        execution = self._remediation_repository.get_execution(
            execution_id=existing.execution_id,
        )
        if execution is None or not self._execution_matches(
            execution=execution, reservation=existing, plan=plan, action=action,
        ):
            return {
                "outcome": "deny",
                "error": "completed_reservation_execution_binding_mismatch",
                "reservation": self._reservation_view(existing),
            }
        response = {
            "outcome": decision.outcome.value if decision is not None else "auto_execute",
            "idempotent": True,
            "reservation": self._reservation_view(existing),
            "execution": execution,
            "execution_id": execution.execution_id,
        }
        if decision is not None:
            response["decision"] = decision
        return response

    @staticmethod
    def _reservation_lease_stale(reservation, *, now) -> bool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _reservation_lease_stale؛ المدخلات المهمة: reservation، now.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if reservation.status not in {"reserved", "in_progress"}:
            return False
        expires_at = getattr(reservation, "expires_at", None)
        if expires_at is None:
            return False
        if expires_at.tzinfo is None and now.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=now.tzinfo)
        return expires_at <= now

    @staticmethod
    def _reservation_matches(*, reservation, plan, action, idempotency_key: str) -> bool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _reservation_matches؛ المدخلات المهمة: reservation، plan، action، idempotency_key.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return (
            reservation.idempotency_key == idempotency_key
            and reservation.plan_id == plan.plan_id
            and reservation.plan_fingerprint == plan.plan_fingerprint
            and reservation.server_id == plan.server_id
            and reservation.action_type == action.action_type
            and reservation.target == action.target
        )

    @staticmethod
    def _execution_matches(*, execution, reservation, plan, action) -> bool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _execution_matches؛ المدخلات المهمة: execution، reservation، plan، action.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return (
            execution.execution_id == reservation.execution_id
            and execution.idempotency_key == reservation.idempotency_key
            and execution.plan_id == plan.plan_id
            and execution.server_id == plan.server_id
            and execution.action_id == (action.action_id or action.action_type)
        )

    def candidates(self):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى candidates؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._candidate_service.list_candidates()

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى list_decisions؛ المدخلات المهمة: plan_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.list_decisions(plan_id=plan_id, limit=min(max(limit, 1), 500))

    def get_decision(self, decision_id: str):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى get_decision؛ المدخلات المهمة: decision_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.get_decision(decision_id)

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى list_reservations؛ المدخلات المهمة: policy_id، plan_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.list_reservations(policy_id=policy_id, plan_id=plan_id, limit=min(max(limit, 1), 500))

    def list_authorizations(self, *, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى list_authorizations؛ المدخلات المهمة: limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.list_authorizations(limit=min(max(limit, 1), 500))

    def list_policy_audit_events(self, *, policy_id: str | None = None, limit: int = 100):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى list_policy_audit_events؛ المدخلات المهمة: policy_id، limit.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.list_all_policy_audit_events(
            policy_id=policy_id, limit=min(max(limit, 1), 500)
        )

    def runtime_state(self, policy_id: str):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى runtime_state؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.get_runtime_state(policy_id)

    def history(self, *, issue_fingerprint: str, action_type: str, target: str):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى history؛ المدخلات المهمة: issue_fingerprint، action_type، target.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)

    def _audit(self, plan_id: str, event_type: str, payload: dict) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _audit؛ المدخلات المهمة: plan_id، event_type، payload.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        try:
            self._remediation_service.audit_autonomous(plan_id=plan_id, event_type=event_type, payload=payload)
        except (OperationalError, ValueError):
            return

    @staticmethod
    def _reservation_view(reservation) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _reservation_view؛ المدخلات المهمة: reservation.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "reservation_id": reservation.reservation_id,
            "idempotency_key": reservation.idempotency_key,
            "status": reservation.status,
            "policy_id": reservation.policy_id,
            "plan_id": reservation.plan_id,
            "plan_fingerprint": reservation.plan_fingerprint,
            "server_id": reservation.server_id,
            "action_type": reservation.action_type,
            "target": reservation.target,
            "authorization_id": reservation.authorization_id,
            "execution_id": reservation.execution_id,
        }

    def _record_runtime(
        self, policy, decision, success: bool, execution_id: str | None,
        *, failure_key: str | None = None,
    ):
        """Record one terminal result with DB-side dedupe and breaker trip.

        The SSH/MCP call has already ended before this method runs.  The
        repository transaction therefore stays short and can safely lock the
        policy/runtime rows while concurrent workers finalize the same result.
        """
        if success:
            recorder = getattr(self._repository, "record_autonomous_success", None)
            if recorder is not None:
                try:
                    return recorder(policy_id=policy.policy_id, policy_version=getattr(decision, "policy_version", None))
                except OperationalError:
                    # Legacy unit schemas may omit the additive Phase 7
                    # policy table; retain their runtime-only compatibility.
                    pass
            return self._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(), consecutive_failures=0,
                triggering_execution_id=None, triggering_decision_id=None,
            )

        recorder = getattr(self._repository, "record_autonomous_failure", None)
        if recorder is None:
            current = self._repository.get_runtime_state(policy.policy_id)
            return self._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(),
                consecutive_failures=int(current.consecutive_failures) + 1,
                suspended_at=utc_now() if getattr(policy, "auto_suspend_on_failure", False) else None,
                suspension_reason="execution_failure" if getattr(policy, "auto_suspend_on_failure", False) else None,
                triggering_execution_id=execution_id or failure_key,
                triggering_decision_id=getattr(decision, "decision_id", None),
            )

        try:
            runtime, counted, tripped, stale_policy = recorder(
                policy_id=policy.policy_id,
                policy_version=getattr(decision, "policy_version", None),
                failure_key=failure_key or execution_id or getattr(decision, "decision_id", None),
                decision_id=getattr(decision, "decision_id", None),
                execution_id=execution_id,
            )
        except OperationalError:
            current = self._repository.get_runtime_state(policy.policy_id)
            return self._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(),
                consecutive_failures=int(current.consecutive_failures) + 1,
                triggering_execution_id=execution_id or failure_key,
                triggering_decision_id=getattr(decision, "decision_id", None),
            )
        if counted:
            self._audit(decision.plan_id, "autonomous_runtime_failure_recorded", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "failure_key": failure_key or execution_id,
                "execution_id": execution_id,
                "consecutive_failures": runtime.consecutive_failures,
            })
        if tripped:
            self._audit(decision.plan_id, "autonomous_circuit_breaker_tripped", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "consecutive_failures": runtime.consecutive_failures,
                "threshold": getattr(policy, "max_consecutive_failures", 1),
            })
            self._audit(decision.plan_id, "autonomous_policy_suspended", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "reason": "consecutive_failure_threshold",
            })
        return runtime

    @staticmethod
    def _single_action(plan):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _single_action؛ المدخلات المهمة: plan.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        actions = [RemediationAction.from_dict(item) for item in (plan.proposed_actions or [])]
        if len(actions) != 1:
            raise ValueError("Phase 7 requires exactly one registered action.")
        return actions[0]

    @staticmethod
    def _history_dict(history):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _history_dict؛ المدخلات المهمة: history.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {"issue_fingerprint": history.issue_fingerprint, "action_type": history.action_type, "target": history.target,
                "supervised_execution_count": history.supervised_execution_count, "verified_success_count": history.verified_success_count,
                "failed_execution_count": history.failed_execution_count, "rollback_failure_count": history.rollback_failure_count,
                "success_rate": history.success_rate, "failure_rate": history.failure_rate}
