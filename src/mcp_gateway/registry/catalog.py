from dataclasses import dataclass


@dataclass(frozen=True)
class McpServerRecord:
    mcp_id: str
    name: str
    url: str


@dataclass(frozen=True)
class GatewayClientRecord:
    client_id: str
    allowed_mcp_ids: tuple[str, ...]


class McpRegistry:
    """Static catalog of downstream app MCPs and allowed callers. Not loaded yet."""

    async def list_servers(self) -> list[McpServerRecord]:
        raise NotImplementedError

    async def resolve(self, mcp_id: str) -> McpServerRecord:
        raise NotImplementedError

    async def resolve_for_tool(self, namespaced_tool: str) -> McpServerRecord:
        raise NotImplementedError

    async def allowed_mcp_ids(self, client_id: str) -> tuple[str, ...]:
        raise NotImplementedError
