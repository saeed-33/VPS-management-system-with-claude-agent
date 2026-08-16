"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.source_location، app.core.policies.diagnostic_policy، app.infrastructure.ssh، app.infrastructure.ssh.client، app.infrastructure.ssh.command_executor.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Protocol

from app.core.contracts.investigation import EvidenceKind, EvidenceReference
from app.capabilities.investigation.source_location import extract_source_locations
from app.core.policies.diagnostic_policy import DiagnosticPolicyResult
from app.infrastructure.ssh import SSHError
from app.infrastructure.ssh.client import SSHClient, SSHConnectionConfig
from app.infrastructure.ssh.command_executor import SSHCommandExecutor


@dataclass(slots=True, frozen=True)
class DiagnosticExecutionOutcome:
    """
    يمثل DiagnosticExecutionOutcome مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    success: bool
    exit_status: int | None
    stdout: str
    stderr: str
    error_message: str | None
    started_at: datetime
    finished_at: datetime
    duration_ms: float


class DiagnosticCommandRunner(Protocol):
    """
    يمثل DiagnosticCommandRunner مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def run(
        self,
        *,
        config: SSHConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: config، tool_id، command_text، timeout_seconds.
        تعيد DiagnosticExecutionOutcome أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class ServerRecord(Protocol):
    """
    يمثل ServerRecord مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    host: str
    port: int
    username: str
    private_key_path: str | None


class ServerRepositoryProtocol(Protocol):
    """
    يمثل ServerRepositoryProtocol مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def get_by_id(self, server_id: int) -> ServerRecord | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: server_id.
        تعيد ServerRecord | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


@dataclass(slots=True, frozen=True)
class EvidenceCollectionRequest:
    """
    يمثل EvidenceCollectionRequest مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    evidence_id: str
    server_id: int
    policy_result: DiagnosticPolicyResult

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty.")
        if self.server_id < 1:
            raise ValueError("server_id must be >= 1.")


class SSHDiagnosticCommandRunner:
    """
    يمثل SSHDiagnosticCommandRunner مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def run(
        self,
        *,
        config: SSHConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: config، tool_id، command_text، timeout_seconds.
        تعيد DiagnosticExecutionOutcome أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        started_at = datetime.now(UTC)
        started_counter = perf_counter()

        try:
            async with SSHClient(config) as ssh_client:
                result = await SSHCommandExecutor(ssh_client).execute(
                    command_id=None,
                    command_name=f"diagnostic:{tool_id}",
                    command_text=command_text,
                    execution_order=1,
                    timeout_seconds=timeout_seconds,
                    fingerprint_strategy="diagnostic_tool",
                    fingerprint_config={"tool_id": tool_id},
                )

            return DiagnosticExecutionOutcome(
                success=result.success,
                exit_status=result.exit_status,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message=result.error_message,
                started_at=result.started_at,
                finished_at=result.finished_at,
                duration_ms=result.duration_ms,
            )

        except (
            SSHError,
            OSError,
            TimeoutError,
            FileNotFoundError,
        ) as exc:
            return DiagnosticExecutionOutcome(
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=round(
                    (perf_counter() - started_counter) * 1000,
                    2,
                ),
            )


class EvidenceCollectionService:
    """
    يمثل EvidenceCollectionService مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        server_repository: ServerRepositoryProtocol,
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
        runner: DiagnosticCommandRunner | None = None,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_repository، default_private_key_path، known_hosts_path، connection_timeout_seconds، runner.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        self._runner = runner or SSHDiagnosticCommandRunner()

    async def collect(
        self,
        request: EvidenceCollectionRequest,
    ) -> EvidenceReference:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى collect؛ المدخلات المهمة: request.
        تعيد EvidenceReference أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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

        config = SSHConnectionConfig(
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _render_excerpt؛ المدخلات المهمة: outcome، limit.
        تعيد tuple[str, bool] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
