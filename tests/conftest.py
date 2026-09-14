import pytest
from fastapi.testclient import TestClient

from mcp_gateway.main import create_app
from mcp_gateway.registry.catalog import McpRegistry
from tests.fakes import FakeDownstreamMcp

ADO_TOOLS = [
    {
        "name": "list_work_items",
        "description": "List Azure DevOps work items",
        "inputSchema": {"type": "object"},
    },
    {
        "name": "delete_project",
        "description": "Delete an Azure DevOps project",
        "inputSchema": {"type": "object"},
    },
]
ORACLE_TOOLS = [
    {
        "name": "query",
        "description": "Run a query against Oracle",
        "inputSchema": {"type": "object"},
    }
]


@pytest.fixture
def registry() -> McpRegistry:
    return McpRegistry.from_yaml("config/mcp-servers.yaml")


@pytest.fixture
def downstream() -> FakeDownstreamMcp:
    return FakeDownstreamMcp({"ado": ADO_TOOLS, "oracle": ORACLE_TOOLS})


@pytest.fixture
def client(registry: McpRegistry, downstream: FakeDownstreamMcp) -> TestClient:
    return TestClient(create_app(registry=registry, downstream=downstream))
