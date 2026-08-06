from collections.abc import Callable
from typing import Awaitable

from langgraph.graph import END, START, StateGraph

from app.agent.graph.state import (
    MonitoringGraphState,
)
from app.agent.monitoring_service import (
    MonitoringService,
)


def build_monitoring_graph(
    monitoring_service: MonitoringService,
):
    async def run_monitoring_node(
        state: MonitoringGraphState,
    ) -> MonitoringGraphState:
        try:
            report = await monitoring_service.run(
                state["server_id"]
            )

            return MonitoringGraphState(
                report=report,
                success=True,
                error_message=None,
            )

        except Exception as exc:
            return MonitoringGraphState(
                success=False,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )

    graph = StateGraph(MonitoringGraphState)

    graph.add_node(
        "run_monitoring",
        run_monitoring_node,
    )

    graph.add_edge(
        START,
        "run_monitoring",
    )

    graph.add_edge(
        "run_monitoring",
        END,
    )

    return graph.compile()