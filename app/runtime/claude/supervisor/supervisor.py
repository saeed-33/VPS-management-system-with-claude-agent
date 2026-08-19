"""منسق تشغيل مراقبة Claude."""
from __future__ import annotations

from .runner import MonitoringRunner

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

