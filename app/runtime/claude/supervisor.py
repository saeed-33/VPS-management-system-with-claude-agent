"""
واجهة الإشراف على تشغيل دورات المراقبة عبر Claude.

تعرض حالة المشغل، وترفض التشغيل عندما يكون runtime معطلًا، وتفوض الدورة إلى
العامل الذي ينفذ مسار المراقبة الفعلي.
"""

from __future__ import annotations

from typing import Protocol


class MonitoringRunner(Protocol):
    """
    عقد لعامل يبدأ دورة مراقبة مرتبطة بسيرفر محدد.
    """
    async def run(self, server_id: int):
        """
        يبدأ دورة المراقبة للسيرفر المحدد ويعيد نتيجتها التشغيلية.
        """
        ...


class ClaudeSupervisor:
    """
    منسق يقرر هل runtime متاح ثم يفوض دورة المراقبة إلى العامل المسجل.
    """
    def __init__(
        self,
        *,
        runner: MonitoringRunner | None,
    ) -> None:
        """
        يسجل العامل الاختياري الذي سينفذ دورات المراقبة.
        """
        self._runner = runner

    @property
    def status(self) -> dict[str, str]:
        """
        يعرض ما إذا كان مشغل Claude متاحًا لتشغيل المراقبة.
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
        يرفض الدورة عند تعطيل runtime ويفوضها إلى العامل عند توفره.
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
