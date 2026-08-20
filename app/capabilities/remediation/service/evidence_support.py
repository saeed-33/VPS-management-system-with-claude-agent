"""دعم جمع أدلة حالة الخدمة والتحقق منها أثناء المعالجة."""
from __future__ import annotations

from uuid import uuid4

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.service_state_observation import ServiceStateObservation


class _RemediationEvidenceMixin:
    """يوفر عمليات جمع دليل الحالة والتحقق من أثر التنفيذ."""

    def _collect_evidence(self, *, plan, execution_id: str | None, server_id: int,
                          service: str, phase: str):
        try:
            observation = self._evidence_collector.collect(
                server_id=server_id,
                service=service,
            )
        except Exception:
            return None
        if not isinstance(observation, ServiceStateObservation):
            return None
        if observation.state == "unknown":
            return None
        return self._repository.create_evidence(
            evidence_id=str(uuid4()),
            plan_id=plan.plan_id,
            execution_id=execution_id,
            server_id=server_id,
            service=service,
            phase=phase,
            observed_state=observation.state,
            metadata={
                "stdout": observation.stdout,
                "stderr": observation.stderr,
                "exit_status": observation.exit_status,
                "error": observation.error,
                **dict(observation.metadata),
            },
        )

    @staticmethod
    def _evidence_belongs_to(evidence, *, plan_id: str, execution_id: str,
                             server_id: int, service: str) -> bool:
        return (
            evidence.plan_id == plan_id
            and evidence.execution_id == execution_id
            and evidence.server_id == server_id
            and evidence.service == service
            and evidence.phase == "before"
            and evidence.observed_state in {"active", "inactive"}
        )

    def _verify_state(self, *, server_id: int, action: RemediationAction,
                      expected_state: str) -> tuple[bool, dict]:
        verify_state = getattr(self._verification_runner, "verify_state", None)
        if callable(verify_state):
            return verify_state(
                server_id=server_id,
                service=action.target,
                expected_state=expected_state,
            )
        if expected_state != "active":
            return False, {
                "expected": expected_state,
                "error": "state_aware_verifier_not_configured",
            }
        return self._verification_runner.verify(
            server_id=server_id,
            action=action,
        )
