from __future__ import annotations

import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )

from app.bootstrap import container
from app.mcp.server import (
    ProjectMcpProtocolServer,
    run_stdio_server,
)


async def main() -> None:
    await run_stdio_server(
        ProjectMcpProtocolServer(
            tool_boundary=(
                container.project_mcp_tool_boundary
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
