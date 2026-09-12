class DownstreamMcpClient:
    """Speaks MCP to a registered per-app MCP server. Not implemented in scaffolding."""

    async def list_tools(self, mcp_id: str) -> list[dict]:
        raise NotImplementedError

    async def call_tool(self, mcp_id: str, tool_name: str, arguments: dict) -> dict:
        raise NotImplementedError
