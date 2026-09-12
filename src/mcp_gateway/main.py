from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from mcp_gateway.api.router import api_router
from mcp_gateway.config import Settings, get_settings
from mcp_gateway.proxy.downstream import DownstreamMcpClient, ToolLister
from mcp_gateway.registry.catalog import McpRegistry


def create_app(
    *,
    settings: Settings | None = None,
    registry: McpRegistry | None = None,
    downstream: ToolLister | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    registry = registry or McpRegistry.from_yaml(settings.registry_path)
    downstream = downstream or DownstreamMcpClient()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        await app.state.downstream.aclose()

    app = FastAPI(
        title="MCP Gateway",
        description="Single MCP front door that routes internal LLMs to per-app MCP servers.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.registry = registry
    app.state.downstream = downstream
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
