from typing import Any

from mcp_gateway.registry.catalog import McpServerRecord


class FakeDownstreamMcp:
    def __init__(self, tools_by_mcp: dict[str, list[dict[str, Any]]]) -> None:
        self.tools_by_mcp = tools_by_mcp

    async def list_tools(self, server: McpServerRecord) -> list[dict[str, Any]]:
        return list(self.tools_by_mcp.get(server.mcp_id, []))

    async def aclose(self) -> None:
        return None
