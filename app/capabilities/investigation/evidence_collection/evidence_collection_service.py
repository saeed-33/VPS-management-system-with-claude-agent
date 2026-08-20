"""Class extracted from evidence_collection during the structure refactor."""

from __future__ import annotations

from app.core.contracts.investigation.diagnostic_connection_config import DiagnosticConnectionConfig
from app.core.contracts.investigation.diagnostic_execution_outcome import DiagnosticExecutionOutcome
from app.core.contracts.investigation.evidence_collection_request import EvidenceCollectionRequest
from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.capabilities.investigation.source_location import extract_source_locations
from app.core.ports.investigation.diagnostic_command_runner import DiagnosticCommandRunnerPort
from app.core.ports.investigation.server_repository import InvestigationServerRepositoryPort

class EvidenceCollectionService:
    """
    ينسق جلب السيرفر وتشغيل الأوامر وحفظ مخرجات الدليل.
    """
    def __init__(
        self,
        *,
        server_repository: InvestigationServerRepositoryPort,
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
        runner: DiagnosticCommandRunnerPort,
    ) -> None:
        """
        يهيئ EvidenceCollectionService ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        if not default_private_key_path.strip():
            raise ValueError(
                "default_private_key_path must not be empty."
            )
        if not known_hosts_path.strip():
            raise ValueError("known_hosts_path must not be empty.")
        if connection_timeout_seconds <= 0:
            raise ValueError(
                "connection_timeout_seconds must be > 0."
            )

        self._server_repository = server_repository
        self._default_private_key_path = default_private_key_path
        self._known_hosts_path = known_hosts_path
        self._connection_timeout_seconds = connection_timeout_seconds
        self._runner = runner

    async def collect(
        self,
        request: EvidenceCollectionRequest,
    ) -> EvidenceReference:
        """
        يجمع الأدلة المطلوبة، يحد المخرجات، ويسجل نتيجة كل أمر.
        """
        policy = request.policy_result

        if not policy.allowed:
            raise PermissionError(
                "Diagnostic evidence collection requires an ALLOW policy result."
            )

        command_text = policy.rendered_command
        timeout_seconds = policy.timeout_seconds
        output_limit_chars = policy.output_limit_chars

        if (
            not command_text
            or timeout_seconds is None
            or output_limit_chars is None
        ):
            raise ValueError(
                "Approved diagnostic policy result has an incomplete execution envelope."
            )

        server = self._server_repository.get_by_id(
            request.server_id
        )

        if server is None:
            raise ValueError(
                f"Server with id {request.server_id} was not found."
            )

        config = DiagnosticConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=(
                server.private_key_path
                or self._default_private_key_path
            ),
            known_hosts_path=self._known_hosts_path,
            connect_timeout_seconds=(
                self._connection_timeout_seconds
            ),
        )

        outcome = await self._runner.run(
            config=config,
            tool_id=policy.tool_id,
            command_text=command_text,
            timeout_seconds=timeout_seconds,
        )

        excerpt, truncated = self._render_excerpt(
            outcome=outcome,
            limit=output_limit_chars,
        )

        locations = extract_source_locations(
            excerpt,
            evidence_ids=(request.evidence_id,),
        )
        metadata = {
            "server_id": request.server_id,
            "specialist_slug": policy.specialist_slug,
            "tool_id": policy.tool_id,
            "command_text": command_text,
            "success": outcome.success,
            "exit_status": outcome.exit_status,
            "error_message": outcome.error_message,
            "started_at": outcome.started_at.isoformat(),
            "finished_at": outcome.finished_at.isoformat(),
            "duration_ms": outcome.duration_ms,
            "timeout_seconds": timeout_seconds,
            "output_limit_chars": output_limit_chars,
            "stdout_chars": len(outcome.stdout),
            "stderr_chars": len(outcome.stderr),
            "excerpt_truncated": truncated,
            "risk": policy.metadata.get("risk"),
            "requires_sudo": policy.metadata.get("requires_sudo"),
        }
        if locations:
            metadata["code_locations"] = [item.to_dict() for item in locations]

        return EvidenceReference(
            evidence_id=request.evidence_id,
            kind=EvidenceKind.COMMAND_RESULT,
            title=(
                f"Diagnostic tool {policy.tool_id} "
                f"on server {request.server_id}"
            ),
            source_id=request.server_id,
            excerpt=excerpt,
            metadata=metadata,
        )

    @staticmethod
    def _render_excerpt(
        *,
        outcome: DiagnosticExecutionOutcome,
        limit: int,
    ) -> tuple[str, bool]:
        """
        يقتطع مخرج الأمر إلى حجم آمن مع الحفاظ على علامة الاقتطاع.
        """
        parts: list[str] = []

        if outcome.stdout:
            parts.append("STDOUT:\n" + outcome.stdout)

        if outcome.stderr:
            parts.append("STDERR:\n" + outcome.stderr)

        if outcome.error_message:
            parts.append("ERROR:\n" + outcome.error_message)

        if not parts:
            parts.append("(command produced no output)")

        text = "\n\n".join(parts)

        if len(text) <= limit:
            return text, False

        suffix = "\n...[truncated]"

        if limit <= len(suffix):
            return text[:limit], True

        return text[: limit - len(suffix)] + suffix, True
