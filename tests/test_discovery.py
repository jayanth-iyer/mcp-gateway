from fastapi.testclient import TestClient


def _tool_names(body: dict) -> list[str]:
    return [tool["name"] for tool in body["result"]["tools"]]


def test_coding_assistant_sees_only_allowed_non_high_risk_ado_tools(client: TestClient) -> None:
    response = client.post(
        "/",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Authorization": "Bearer coding-assistant-dev-token"},
    )
    assert response.status_code == 200
    body = response.json()
    names = _tool_names(body)
    assert "ado.list_work_items" in names
    assert all(not name.startswith("oracle.") for name in names)
    assert "ado.delete_project" not in names


def test_finance_agent_sees_only_oracle_tools(client: TestClient) -> None:
    response = client.post(
        "/",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        headers={"Authorization": "Bearer finance-agent-dev-token"},
    )
    names = _tool_names(response.json())
    assert names == ["oracle.query"]


def test_admin_sees_high_risk_tools_from_allowed_mcps(client: TestClient) -> None:
    response = client.post(
        "/",
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
        headers={"Authorization": "Bearer platform-admin-dev-token"},
    )
    names = _tool_names(response.json())
    assert "ado.list_work_items" in names
    assert "ado.delete_project" in names
    assert "oracle.query" in names


def test_tools_list_without_token_is_unauthorized(client: TestClient) -> None:
    response = client.post("/", json={"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
    body = response.json()
    assert body["error"]["code"] == -32000
    assert body["error"]["message"] == "Unauthorized"


def test_tools_list_with_unknown_token_is_unauthorized(client: TestClient) -> None:
    response = client.post(
        "/",
        json={"jsonrpc": "2.0", "id": 5, "method": "tools/list"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.json()["error"]["code"] == -32000
