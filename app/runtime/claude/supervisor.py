from __future__ import annotations

from typing import Protocol


class MonitoringRunner(Protocol):
    async def run(self, server_id: int):
        ...


class ClaudeSupervisor:
    def __init__(
        self,
        *,
        runner: MonitoringRunner,
    ) -> None:
        self._runner = runner

    @property
    def status(self) -> dict[str, str]:
        return {
            "runtime": "claude",
            "state": "active",
        }

    async def run(
        self,
        server_id: int,
    ):
        return await self._runner.run(
            server_id=server_id
        )
