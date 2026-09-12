# MCP Gateway

A single MCP server for **internal LLM services**. Those services call only the gateway; the gateway routes to per-app MCPs (ADO, Oracle, and the rest of the estate).

```
Internal LLM  →  MCP Gateway (one MCP)  →  ADO MCP, Oracle MCP, … (~50 app MCPs)
```

v1 also applies identity, redaction, authorization, and audit on that hop. Downstream MCP URLs and which caller may use which MCP live in static config (`config/mcp-servers.yaml`). IDE clients are out of scope.

This branch is **initial scaffolding only**. Registry load, routing, and governance are stubbed.

See [docs/mcp-gateway.md](docs/mcp-gateway.md) for locked decisions and BDD.

## Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3.12+ | Matches the team preference; strong libraries for HTTP proxies, policy, and data masking |
| HTTP API | FastAPI + Uvicorn | Native async, typed request models, good fit for a JSON-RPC/MCP front door on port 8000 |
| Settings | Pydantic Settings | Env-driven config (`MCP_GATEWAY_*`) without a custom loader |
| Registry | Static YAML | `config/mcp-servers.yaml` — no dynamic registration in v1 |
| Audit store | SQLAlchemy 2 (asyncio) + aiosqlite | Local SQLite audit table; same engine can move to Postgres |
| Downstream MCP | httpx | Async client for MCP JSON-RPC against registered app MCPs |
| Tests | pytest + pytest-asyncio | FastAPI `TestClient` for the health/JSON-RPC stubs; BDD scenarios live under `tests/features/` |
| Lint | Ruff | Single tool for lint and import sorting |

## Layout

```
config/mcp-servers.yaml    # Static registry (ADO, Oracle examples)
src/mcp_gateway/
  main.py                  # FastAPI app factory and uvicorn entrypoint
  config.py                # Settings
  api/                     # HTTP: /health and JSON-RPC POST /
  auth/                    # Token → internal LLM caller (stub)
  governance/              # Redaction + authorization (stubs)
  audit/                   # Append-only audit store (stub)
  registry/                # Load static YAML catalog (stub)
  proxy/                   # MCP client to app MCPs (stub)
tests/
  features/                # Gherkin aligned with the architecture doc
```

## Local run

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --group dev
cp .env.example .env
uv run mcp-gateway
```

Service listens on `http://localhost:8000`.

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/ \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

```bash
uv run pytest
```
