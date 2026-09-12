import uvicorn
from fastapi import FastAPI

from mcp_gateway.api.router import api_router
from mcp_gateway.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="MCP Gateway",
        description="Single MCP front door that routes AI clients to per-app MCP servers.",
        version="0.1.0",
    )
    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "mcp_gateway.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=False,
    )
