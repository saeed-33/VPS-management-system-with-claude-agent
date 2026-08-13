from __future__ import annotations

from typing import Any

from app.interfaces.mcp.schemas import ProjectToolResult
from app.interfaces.mcp.serializers import serialize_value


class RemediationToolsMixin:
    async def _attempt_autonomous_remediation(self, arguments: dict[str, Any]) -> ProjectToolResult:
        self._require_dependency(self._autonomous_execution_service, "autonomous_execution_service")
        result = self._autonomous_execution_service.attempt(
            plan_id=self._required_string(arguments, "plan_id"),
            actor="claude-autonomous-policy",
        )
        outcome = result.get("outcome")
        return ProjectToolResult(
            tool_id="attempt_autonomous_remediation",
            success=outcome == "auto_execute" and bool(result.get("result", {}).get("applied")),
            data=serialize_value(result),
            error_code=None if outcome == "auto_execute" and result.get("result", {}).get("applied") else outcome,
            error_message=None if outcome == "auto_execute" and result.get("result", {}).get("applied") else "Autonomous policy did not authorize a successful execution.",
        )

    async def _propose_remediation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        proposal = (
            self._remediation_service
            .propose_remediation(
                investigation_id=self._required_string(
                    arguments,
                    "investigation_id",
                ),
                problem_summary=self._required_string(
                    arguments,
                    "problem_summary",
                ),
                diagnosis_claim_ids=(
                    self._required_string_list(
                        arguments,
                        "diagnosis_claim_ids",
                    )
                ),
                evidence_ids=self._required_string_list(
                    arguments,
                    "evidence_ids",
                ),
            )
        )

        return ProjectToolResult(
            tool_id="propose_remediation",
            success=True,
            data={
                "proposal": serialize_value(
                    proposal
                )
            },
        )

    async def _create_remediation_plan(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        actions = arguments.get(
            "proposed_actions"
        )
        if not isinstance(actions, list):
            raise ValueError(
                "proposed_actions must be a list."
            )

        plan = (
            self._remediation_service
            .create_plan(
                investigation_id=self._required_string(
                    arguments,
                    "investigation_id",
                ),
                title=self._required_string(
                    arguments,
                    "title",
                ),
                problem_summary=self._required_string(
                    arguments,
                    "problem_summary",
                ),
                proposed_actions=actions,
                diagnosis_claim_ids=(
                    self._required_string_list(
                        arguments,
                        "diagnosis_claim_ids",
                    )
                ),
                evidence_ids=self._required_string_list(
                    arguments,
                    "evidence_ids",
                ),
                risk_level=str(
                    arguments.get(
                        "risk_level",
                        "medium",
                    )
                ),
                rollback_plan=arguments.get(
                    "rollback_plan"
                ),
                plan_id=arguments.get("plan_id"),
                server_id=arguments.get("server_id"),
            )
        )

        return ProjectToolResult(
            tool_id="create_remediation_plan",
            success=True,
            data={
                "plan": serialize_value(plan)
            },
        )

    async def _test_remediation_in_sandbox(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        plan_id = self._required_string(arguments, "plan_id")
        if all(key in arguments for key in ("target_server_id", "target_server_name", "target_service")):
            result = self._remediation_service.validate_in_isolated_sandbox(
                plan_id=plan_id,
                target_server_id=int(arguments["target_server_id"]),
                target_server_name=self._required_string(arguments, "target_server_name"),
                target_service=self._required_string(arguments, "target_service"),
            )
        else:
            # Preserve the Phase 5 dry-run contract for existing callers.
            result = self._remediation_service.test_in_sandbox(plan_id=plan_id)

        return ProjectToolResult(
            tool_id="test_remediation_in_sandbox",
            success=getattr(result, "status", "") in {"passed", "sandbox_passed"},
            data={
                "sandbox_result": serialize_value(
                    result
                ),
                "sandbox_validation": serialize_value(
                    result if hasattr(result, "validation_id") else None
                ),
            },
            error_code=None if getattr(result, "status", "") in {"passed", "sandbox_passed"} else "sandbox_validation_failed",
            error_message=None if getattr(result, "status", "") in {"passed", "sandbox_passed"} else getattr(result, "failure_reason", "Sandbox validation failed."),
        )

    async def _get_sandbox_result(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        result_id = arguments.get("result_id")
        validation_id = arguments.get("validation_id")
        plan_id = arguments.get("plan_id")
        for name, value in (("result_id", result_id), ("validation_id", validation_id), ("plan_id", plan_id)):
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{name} must be a string.")

        result = (
            self._remediation_service
            .get_sandbox_result(
                result_id,
                plan_id=plan_id,
            )
        )
        validation = None
        if validation_id is not None:
            validation = self._remediation_service.get_sandbox_validation(validation_id=validation_id)
        elif plan_id is not None:
            validation = self._remediation_service.get_sandbox_validation(plan_id=plan_id)
        if result is None:
            if validation is not None:
                return ProjectToolResult(
                    tool_id="get_sandbox_result", success=True,
                    data={"sandbox_validation": serialize_value(validation)},
                )
            return ProjectToolResult(
                tool_id="get_sandbox_result",
                success=False,
                error_code="sandbox_result_not_found",
                error_message=(
                    "Sandbox result was not found."
                ),
            )

        return ProjectToolResult(
            tool_id="get_sandbox_result",
            success=True,
            data={
                "sandbox_result": serialize_value(result),
                "sandbox_validation": serialize_value(validation),
            },
        )

    async def _request_user_approval(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        plan = (
            self._remediation_service
            .request_approval(
                plan_id=self._required_string(
                    arguments,
                    "plan_id",
                ),
                expires_in_seconds=int(
                    arguments.get("expires_in_seconds", 3600)
                ),
                scope=(
                    arguments.get("scope")
                    if isinstance(arguments.get("scope"), dict)
                    else None
                ),
            )
        )

        return ProjectToolResult(
            tool_id="request_user_approval",
            success=True,
            data={
                "plan": serialize_value(plan),
                "approval_required": True,
            },
        )

    async def _apply_approved_remediation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        outcome = (
            self._remediation_service
            .apply_approved(
                plan_id=self._required_string(
                    arguments,
                    "plan_id",
                ),
                approval_id=arguments.get("approval_id"),
                approved_by=arguments.get(
                    "approved_by"
                ),
                server_id=arguments.get("server_id"),
                actor=arguments.get("actor"),
                idempotency_key=arguments.get("idempotency_key"),
                runtime_session_id=arguments.get("runtime_session_id"),
                agent_job_id=arguments.get("agent_job_id"),
            )
        )

        return ProjectToolResult(
            tool_id="apply_approved_remediation",
            success=bool(
                outcome.get("applied")
            ),
            data={
                "outcome": serialize_value(
                    outcome
                )
            },
            error_code=(
                None
                if outcome.get("applied")
                else str(
                    outcome.get(
                        "blocked_reason",
                        "remediation_blocked",
                    )
                )
            ),
            error_message=(
                None
                if outcome.get("applied")
                else str(
                    outcome.get(
                        "message",
                        "Remediation was blocked.",
                    )
                )
            ),
        )
