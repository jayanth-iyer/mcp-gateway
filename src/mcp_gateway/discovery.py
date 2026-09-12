from typing import Any

from mcp_gateway.auth.identity import IdentityContext
from mcp_gateway.governance.authorization import can_execute_tool
from mcp_gateway.proxy.downstream import ToolLister
from mcp_gateway.registry.catalog import McpRegistry


def namespace_tool(mcp_id: str, tool: dict[str, Any]) -> dict[str, Any]:
    namespaced = dict(tool)
    original_name = str(tool.get("name", ""))
    namespaced["name"] = f"{mcp_id}.{original_name}"
    return namespaced


async def list_visible_tools(
    identity: IdentityContext,
    registry: McpRegistry,
    downstream: ToolLister,
) -> list[dict[str, Any]]:
    visible: list[dict[str, Any]] = []
    for mcp_id in identity.allowed_mcp_ids:
        server = registry.resolve(mcp_id)
        for tool in await downstream.list_tools(server):
            tool_name = str(tool.get("name", ""))
            if can_execute_tool(identity, server, tool_name):
                visible.append(namespace_tool(server.mcp_id, tool))
    return visible
