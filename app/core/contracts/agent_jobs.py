"""
عقود وDTOs مشتركة لنقل البيانات بين الطبقات.

الموقع في المعمارية: Core application contracts.
يُستدعى بواسطة: capabilities وinterfaces وadapters.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ I/O أو workflow.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class CreateAgentJobDTO:
    """
    يمثل CreateAgentJobDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    job_id: str
    job_type: str
    status: str
    server_id: int | None = None
    claude_session_id: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if (
            self.server_id is not None
            and self.server_id < 1
        ):
            raise ValueError(
                "server_id must be >= 1 when provided."
            )


@dataclass(slots=True, frozen=True)
class UpdateAgentJobDTO:
    """
    يمثل UpdateAgentJobDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    status: str
    claude_session_id: str | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )
