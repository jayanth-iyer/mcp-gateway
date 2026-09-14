from typing import Any, Protocol

import httpx

from mcp_gateway.registry.catalog import McpServerRecord


class ToolLister(Protocol):
    async def list_tools(self, server: McpServerRecord) -> list[dict[str, Any]]: ...

    async def aclose(self) -> None: ...


class DownstreamMcpClient:
    """Speaks MCP JSON-RPC to a registered per-app MCP server."""

    def __init__(self, http: httpx.AsyncClient | None = None) -> None:
        self._http = http or httpx.AsyncClient(timeout=10.0)
        self._owns_http = http is None

    async def list_tools(self, server: McpServerRecord) -> list[dict[str, Any]]:
        response = await self._http.post(
            server.url,
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Downstream MCP {server.mcp_id} returned a non-object body.")
        if "error" in payload:
            message = payload["error"].get("message", "tools/list failed")
            raise ValueError(f"Downstream MCP {server.mcp_id}: {message}")
        result = payload.get("result") or {}
        tools = result.get("tools") or []
        if not isinstance(tools, list):
            raise ValueError(f"Downstream MCP {server.mcp_id} returned an invalid tools list.")
        return tools

    async def call_tool(self, mcp_id: str, tool_name: str, arguments: dict) -> dict:
        raise NotImplementedError

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()
