from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RegistryError(ValueError):
    """Raised when the static MCP registry file is invalid."""


@dataclass(frozen=True)
class McpServerRecord:
    mcp_id: str
    name: str
    url: str
    high_risk_tools: tuple[str, ...]


@dataclass(frozen=True)
class GatewayClientRecord:
    client_id: str
    token: str
    roles: tuple[str, ...]
    allowed_mcp_ids: tuple[str, ...]


class McpRegistry:
    """Static catalog of downstream app MCPs and allowed callers."""

    def __init__(
        self,
        servers: list[McpServerRecord],
        clients: list[GatewayClientRecord],
    ) -> None:
        self._servers = {server.mcp_id: server for server in servers}
        self._clients_by_id = {client.client_id: client for client in clients}
        self._clients_by_token = {client.token: client for client in clients}

    @classmethod
    def from_yaml(cls, path: str | Path) -> McpRegistry:
        registry_path = Path(path)
        payload = yaml.safe_load(registry_path.read_text())
        if not isinstance(payload, dict):
            raise RegistryError("Registry file must be a YAML mapping.")
        return cls.from_dict(payload)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> McpRegistry:
        servers = [_parse_server(item) for item in payload.get("servers") or []]
        clients = [_parse_client(item) for item in payload.get("clients") or []]
        _validate(servers, clients)
        return cls(servers, clients)

    def list_servers(self) -> list[McpServerRecord]:
        return list(self._servers.values())

    def resolve(self, mcp_id: str) -> McpServerRecord:
        try:
            return self._servers[mcp_id]
        except KeyError as exc:
            raise KeyError(f"Unknown MCP id: {mcp_id}") from exc

    def resolve_for_tool(self, namespaced_tool: str) -> McpServerRecord:
        mcp_id, _, _tool_name = namespaced_tool.partition(".")
        if not _tool_name:
            raise KeyError(f"Tool name is not namespaced: {namespaced_tool}")
        return self.resolve(mcp_id)

    def client_for_token(self, token: str) -> GatewayClientRecord | None:
        return self._clients_by_token.get(token)

    def allowed_mcp_ids(self, client_id: str) -> tuple[str, ...]:
        client = self._clients_by_id.get(client_id)
        if client is None:
            raise KeyError(f"Unknown client id: {client_id}")
        return client.allowed_mcp_ids


def _parse_server(item: Any) -> McpServerRecord:
    if not isinstance(item, dict):
        raise RegistryError("Each server must be a mapping.")
    mcp_id = str(item["id"])
    return McpServerRecord(
        mcp_id=mcp_id,
        name=str(item.get("name") or mcp_id),
        url=str(item["url"]),
        high_risk_tools=tuple(str(name) for name in item.get("high_risk_tools") or []),
    )


def _parse_client(item: Any) -> GatewayClientRecord:
    if not isinstance(item, dict):
        raise RegistryError("Each client must be a mapping.")
    return GatewayClientRecord(
        client_id=str(item["id"]),
        token=str(item["token"]),
        roles=tuple(str(role) for role in item.get("roles") or []),
        allowed_mcp_ids=tuple(str(mcp_id) for mcp_id in item.get("allowed_mcp_ids") or []),
    )


def _validate(servers: list[McpServerRecord], clients: list[GatewayClientRecord]) -> None:
    server_ids = [server.mcp_id for server in servers]
    if len(server_ids) != len(set(server_ids)):
        raise RegistryError("MCP server ids must be unique.")

    client_ids = [client.client_id for client in clients]
    if len(client_ids) != len(set(client_ids)):
        raise RegistryError("Client ids must be unique.")

    tokens = [client.token for client in clients]
    if len(tokens) != len(set(tokens)):
        raise RegistryError("Client tokens must be unique.")

    known = set(server_ids)
    for client in clients:
        unknown = [mcp_id for mcp_id in client.allowed_mcp_ids if mcp_id not in known]
        if unknown:
            raise RegistryError(
                f"Client {client.client_id} references unknown MCP ids: {', '.join(unknown)}"
            )
