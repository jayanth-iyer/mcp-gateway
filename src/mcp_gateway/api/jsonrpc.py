from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["mcp"])

JSONRPC_NOT_IMPLEMENTED = -32601


@router.post("/")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """Inbound MCP JSON-RPC. AI clients talk only to this server; routing is stubbed."""
    body = await request.json()
    request_id = body.get("id") if isinstance(body, dict) else None
    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": JSONRPC_NOT_IMPLEMENTED,
                "message": "MCP Gateway scaffolding: method handling is not implemented yet.",
            },
        }
    )
