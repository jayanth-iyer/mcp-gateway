# MCP Gateway
**v1 product framing and BDD (scaffolding)**

---

## 1. Executive Summary

Enterprises will stand up an MCP server per application (Azure DevOps, Oracle, and dozens more). Internal LLM services cannot be configured with 50 MCP endpoints. They need one MCP.

The **MCP Gateway** is that front door. It is itself an MCP server. Internal LLM services call only the gateway. The gateway uses a **static registry** of downstream per-app MCPs, routes each call, and applies identity, redaction, authorization, and audit on that hop.

```
Internal LLM service  →  MCP Gateway (one MCP)  →  ADO MCP, Oracle MCP, … (≈50 app MCPs)
```

Out of scope for now: IDE / desktop MCP clients (Cursor, Claude Desktop). Downstream systems are other MCP servers, not raw APIs.

---

## 2. Locked decisions (v1)

| Topic | Decision |
| --- | --- |
| Why it exists | Avoid configuring every LLM with every app MCP |
| Clients | Internal LLM services only |
| Downstream | Per-app MCP servers (examples: ADO MCP, Oracle MCP) |
| Registry | Static config (`config/mcp-servers.yaml`) |
| Governance | All of it: identity, tool filtering, authorization, PII/credential redaction, WORM-style audit |
| `tools/list` | Namespaced union of tools from MCPs the caller is allowed to use (`ado.list_work_items`, `oracle.query`) |
| `tools/call` | Strip the `{mcp_id}.` prefix, forward to that MCP |

A given LLM service is not shown all 50 MCPs. Static config lists `allowed_mcp_ids` per caller so each model only sees the app MCPs it needs.

---

## 3. Request path

1. Internal LLM sends MCP JSON-RPC to the gateway (`tools/list` or `tools/call`) with an API token.
2. Gateway resolves the token to an identity and the allowed MCP ids.
3. **List:** aggregate `tools/list` from those MCPs, prefix tool names with `mcp_id`.
4. **Call:** authorize the tool, redact PII/credentials in the payload, forward to the matching app MCP, redact the response if needed, write an audit row, return the result.
5. High-risk tools that the identity cannot execute are omitted from list and rejected on call (JSON-RPC `-32001`).

---

## 4. Feature Specification (BDD User Stories)

```gherkin
Feature: MCP Gateway for internal LLM services
  As an Enterprise Security Engineer
  I want internal LLM services to call one MCP that routes to per-app MCPs
  So that we do not configure 50 MCP endpoints per model, and so that PII is masked, unauthorized tools are blocked, and calls are audited.

  Background:
    Given the MCP Gateway service is running locally on "http://localhost:8000"
    And the static registry includes MCP servers "ado" and "oracle"
    And the Gateway is connected to a SQLite audit log database

  @discovery @mcp-protocol
  Scenario: Internal LLM discovers tools from allowed app MCPs only
    Given an internal LLM service sends a JSON-RPC "tools/list" request with a valid API token for caller "coding_assistant"
    And caller "coding_assistant" is allowed to use MCP "ado" but not "oracle"
    When the Gateway processes the discovery request
    Then the Gateway should return namespaced tools including "ado.list_work_items"
    And tools from MCP "oracle" should be excluded from the list
    And high-risk tools the caller cannot execute should be excluded from the list

  @routing
  Scenario: Gateway forwards a call to the matching app MCP
    Given an internal LLM service invokes tool "ado.list_work_items"
    And caller "coding_assistant" is allowed to use MCP "ado"
    When the Gateway routes the request
    Then the Gateway should call tool "list_work_items" on the "ado" MCP

  @governance @redaction
  Scenario Outline: Redact sensitive information before forwarding to an app MCP
    Given an internal LLM service invokes tool "oracle.query" with payload "<RawPayload>"
    When the Gateway governance middleware evaluates the request payload
    Then the payload passed to the "oracle" MCP must match "<SanitizedPayload>"

    Examples:
      | RawPayload                                                  | SanitizedPayload                                                 |
      | Query user where ssn = '999-00-1234'                        | Query user where ssn = '[REDACTED_PII]'                          |
      | SELECT * FROM accounts WHERE api_key = 'sk_live_abc123'     | SELECT * FROM accounts WHERE api_key = '[REDACTED_CREDENTIAL]'   |

  @authorization @security
  Scenario: Block unauthorized or high-risk tool execution
    Given an internal LLM service issues an MCP tool call "ado.delete_project"
    And caller "coding_assistant" does not hold the "Admin" role
    When the Gateway interceptor checks permission policies
    Then the request should be rejected with JSON-RPC error code -32001
    And the response message should state "Access Denied: High-risk action requires human approval."

  @audit @compliance
  Scenario: Record tamper-proof audit trail for invoked tools
    Given caller "coding_assistant" successfully invokes tool "ado.list_work_items"
    When the downstream "ado" MCP execution completes with status "200 OK"
    Then an audit record should be written to the local SQLite audit table
    And the record must contain "timestamp", "client_id", "tool_name", "mcp_id", "prompt_hash", and "execution_latency_ms"
```
