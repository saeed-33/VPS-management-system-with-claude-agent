from __future__ import annotations

from typing import Protocol


class MonitoringRunner(Protocol):
    async def run(self, server_id: int):
        ...


class ClaudeSupervisor:
    def __init__(
        self,
        *,
        runner: MonitoringRunner | None,
    ) -> None:
        self._runner = runner

    @property
    def status(self) -> dict[str, str]:
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
        if self._runner is None:
            raise RuntimeError(
                "Claude operational monitoring runtime is disabled. "
                "Set CLAUDE_RUNTIME_ENABLED=true to run scheduled "
                "monitoring cycles."
            )

        return await self._runner.run(
            server_id=server_id
        )
