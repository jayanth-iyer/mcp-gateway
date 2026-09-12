from mcp_gateway.auth.identity import IdentityContext


async def authorize_tool_call(identity: IdentityContext, tool_name: str) -> None:
    """Enforce role policies for tool execution. Not implemented in scaffolding."""
    raise NotImplementedError
