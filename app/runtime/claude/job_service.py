"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: app.runtime.claude.models، app.infrastructure.database.repositories.agent_job_repository، app.core.contracts.agent_jobs.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
)
from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)
from app.core.contracts.agent_jobs import (
    CreateAgentJobDTO,
    UpdateAgentJobDTO,
)


class ClaudeAgentJobService:
    """
    يمثل ClaudeAgentJobService مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        repository: AgentJobRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def create_from_request(
        self,
        request: ClaudeRuntimeRequest,
        *,
        server_id: int | None = None,
    ):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى create_from_request؛ المدخلات المهمة: request، server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.create(
            CreateAgentJobDTO(
                job_id=request.job_id,
                job_type=request.job_type,
                server_id=server_id,
                status=(
                    ClaudeJobStatus.QUEUED.value
                ),
                metadata={
                    "context": dict(
                        request.context
                    ),
                    "max_turns": request.max_turns,
                    "allowed_tools": list(
                        request.allowed_tools
                    ),
                    **dict(
                        request.metadata
                    ),
                },
            )
        )

    def mark_running(
        self,
        *,
        job_id: str,
        session_id: str | None = None,
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى mark_running؛ المدخلات المهمة: job_id، session_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.update(
            job_id,
            UpdateAgentJobDTO(
                status=(
                    ClaudeJobStatus.RUNNING.value
                ),
                claude_session_id=session_id,
            ),
        )

    def complete_from_result(
        self,
        result: ClaudeRuntimeResult,
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى complete_from_result؛ المدخلات المهمة: result.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.update(
            result.job_id,
            UpdateAgentJobDTO(
                status=result.status.value,
                claude_session_id=result.session_id,
                completed_at=datetime.now(
                    timezone.utc
                ),
                error_code=result.error_code,
                error_message=result.error_message,
                turn_count=result.turn_count,
                tool_call_count=(
                    result.tool_call_count
                ),
                usage_metadata=dict(
                    result.usage_metadata
                ),
            ),
        )

    def recover_interrupted_jobs(
        self,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى recover_interrupted_jobs؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return (
            self._repository
            .mark_unfinished_after_restart(
                statuses=(
                    ClaudeJobStatus.QUEUED.value,
                    ClaudeJobStatus.RUNNING.value,
                ),
                failed_status=(
                    ClaudeJobStatus.FAILED.value
                ),
                error_code=(
                    "interrupted_after_restart"
                ),
                error_message=(
                    "Claude agent job was queued or "
                    "running during application restart."
                ),
            )
        )
