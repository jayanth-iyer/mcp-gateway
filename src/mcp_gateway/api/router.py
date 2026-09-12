from fastapi import APIRouter

from mcp_gateway.api.health import router as health_router
from mcp_gateway.api.jsonrpc import router as jsonrpc_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(jsonrpc_router)
