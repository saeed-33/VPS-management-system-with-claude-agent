"""Validated native Claude CLI process command contract."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.runtime.claude.models import ClaudeRuntimeRequest


@dataclass(slots=True, frozen=True)
class ClaudeProcessCommand:
    """
    يمثل ClaudeProcessCommand مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    argv: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.argv:
            raise ValueError("Claude process argv must not be empty.")

        for item in self.argv:
            if not isinstance(item, str) or not item:
                raise ValueError(
                    "Claude process argv entries must be non-empty strings."
                )

        if self.cwd is not None:
            object.__setattr__(self, "cwd", Path(self.cwd).resolve())


class ClaudeProcessCommandBuilder(Protocol):
    """
    يمثل ClaudeProcessCommandBuilder مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def build(self, request: ClaudeRuntimeRequest) -> ClaudeProcessCommand:
        """Build one process command without executing it."""
