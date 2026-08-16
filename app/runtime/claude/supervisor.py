"""
ينسق تشغيل دورة مراقبة واحدة عبر Claude Runtime.

الموقع في المعمارية:
Claude Supervisor → session/monitoring runner → Python capability.
يعتمد هذا الحد على runner محقون؛ أما تنفيذ SSH والحفظ فيبقى داخل طبقات
المراقبة والبنية التحتية، وليس داخل الـSupervisor نفسه.
"""

from __future__ import annotations

from typing import Protocol


class MonitoringRunner(Protocol):
    """
    يمثل MonitoringRunner مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def run(self, server_id: int):
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class ClaudeSupervisor:
    """
    يمثل ClaudeSupervisor مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        runner: MonitoringRunner | None,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: runner.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._runner = runner

    @property
    def status(self) -> dict[str, str]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى status؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict[str, str] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "runtime": "claude",
            "state": (
                "active"
                if self._runner is not None
                else "disabled"
            ),
        }

    async def run(
        self,
        server_id: int,
    ):
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self._runner is None:
            raise RuntimeError(
                "Claude operational monitoring runtime is disabled. "
                "Set CLAUDE_RUNTIME_ENABLED=true to run scheduled "
                "monitoring cycles."
            )

        return await self._runner.run(
            server_id=server_id
        )
