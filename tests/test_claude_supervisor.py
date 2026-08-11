import asyncio

from app.runtime.claude import ClaudeSupervisor


class Runner:
    def __init__(self):
        self.calls = []

    async def run(
        self,
        server_id,
    ):
        self.calls.append(server_id)
        return {
            "runtime": "claude",
            "server_id": server_id,
        }


def test_supervisor_delegates_monitoring_cycle():
    runner = Runner()
    supervisor = ClaudeSupervisor(
        runner=runner,
    )

    result = asyncio.run(
        supervisor.run(7)
    )

    assert result == {
        "runtime": "claude",
        "server_id": 7,
    }
    assert runner.calls == [7]


def test_supervisor_reports_runtime_status():
    supervisor = ClaudeSupervisor(
        runner=Runner(),
    )

    assert supervisor.status == {
        "runtime": "claude",
        "state": "active",
    }
