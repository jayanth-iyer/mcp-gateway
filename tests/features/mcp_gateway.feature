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
      | RawPayload                                              | SanitizedPayload                                               |
      | Query user where ssn = '999-00-1234'                    | Query user where ssn = '[REDACTED_PII]'                        |
      | SELECT * FROM accounts WHERE api_key = 'sk_live_abc123' | SELECT * FROM accounts WHERE api_key = '[REDACTED_CREDENTIAL]' |

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
