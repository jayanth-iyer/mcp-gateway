from dataclasses import dataclass

from mcp_gateway.registry.catalog import McpRegistry


@dataclass(frozen=True)
class IdentityContext:
    client_id: str
    roles: tuple[str, ...]
    token: str
    allowed_mcp_ids: tuple[str, ...]


def parse_bearer_token(authorization_header: str | None) -> str | None:
    if authorization_header is None:
        return None
    value = authorization_header.strip()
    if not value:
        return None
    prefix = "Bearer "
    if value.startswith(prefix):
        token = value[len(prefix) :].strip()
        return token or None
    return value


def resolve_identity(
    authorization_header: str | None,
    registry: McpRegistry,
) -> IdentityContext | None:
    token = parse_bearer_token(authorization_header)
    if token is None:
        return None
    client = registry.client_for_token(token)
    if client is None:
        return None
    return IdentityContext(
        client_id=client.client_id,
        roles=client.roles,
        token=token,
        allowed_mcp_ids=client.allowed_mcp_ids,
    )
