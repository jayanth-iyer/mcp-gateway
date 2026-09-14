from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from mcp_gateway.auth.identity import resolve_identity
from mcp_gateway.discovery import list_visible_tools

router = APIRouter(tags=["mcp"])

JSONRPC_PARSE_ERROR = -32700
JSONRPC_UNAUTHORIZED = -32000
JSONRPC_INTERNAL_ERROR = -32603
JSONRPC_NOT_IMPLEMENTED = -32601


def _jsonrpc_error(request_id: Any, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
    )


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})


@router.post("/")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Inbound MCP JSON-RPC. Internal LLM services talk only to this server."""
    body = await request.json()
    if not isinstance(body, dict):
        return _jsonrpc_error(None, JSONRPC_PARSE_ERROR, "Invalid JSON-RPC request.")

    request_id = body.get("id")
    method = body.get("method")
    if method != "tools/list":
        return _jsonrpc_error(
            request_id,
            JSONRPC_NOT_IMPLEMENTED,
            "MCP Gateway: method handling is not implemented yet.",
        )

    identity = resolve_identity(request.headers.get("authorization"), request.app.state.registry)
    if identity is None:
        return _jsonrpc_error(request_id, JSONRPC_UNAUTHORIZED, "Unauthorized")

    try:
        tools = await list_visible_tools(
            identity,
            request.app.state.registry,
            request.app.state.downstream,
        )
    except Exception as exc:
        return _jsonrpc_error(request_id, JSONRPC_INTERNAL_ERROR, str(exc))

    return _jsonrpc_result(request_id, {"tools": tools})
