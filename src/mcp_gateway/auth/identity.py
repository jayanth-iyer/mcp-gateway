from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityContext:
    client_id: str
    roles: tuple[str, ...]
    token: str


async def resolve_identity(authorization_header: str | None) -> IdentityContext | None:
    """Map an inbound API token to an internal LLM caller. Not implemented in scaffolding."""
    raise NotImplementedError
