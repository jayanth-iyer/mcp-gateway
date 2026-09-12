from mcp_gateway.auth.identity import IdentityContext
from mcp_gateway.registry.catalog import McpServerRecord

ADMIN_ROLE = "Admin"


def is_high_risk_tool(server: McpServerRecord, tool_name: str) -> bool:
    return tool_name in server.high_risk_tools


def can_execute_tool(identity: IdentityContext, server: McpServerRecord, tool_name: str) -> bool:
    if not is_high_risk_tool(server, tool_name):
        return True
    return ADMIN_ROLE in identity.roles


async def authorize_tool_call(identity: IdentityContext, tool_name: str) -> None:
    """Reject unauthorized tools/call. Implemented with feature 3, not discovery."""
    raise NotImplementedError
