# CLAUDE.md

## Project Overview

A LangChain + LangGraph agent that connects to multiple MCP (Model Context Protocol) servers via streamable HTTP, featuring Human-in-the-loop (HITL) confirmation for sensitive operations. The agent is named "周香" and acts as a navigation and device-control assistant.

The name includes "deepeval-trajectory-eval" — this project is designed as a test bed for evaluating agent trajectories (tool call sequences) using DeepEval.

---

## CLI Commands

All commands use `uv run` (the project uses [uv](https://github.com/astral-sh/uv) as the package manager).

### Setup

```bash
uv sync                          # Install all dependencies
cp .env.example .env             # Create env file, then fill in API keys
```

### Run Services

```bash
# Step 1: Start the custom MCP server (must be running before the agent)
uv run python -m agent_call.custom_mcp_server

# Step 2a (recommended): Start the LangGraph dev server with Studio UI
uv run langgraph dev

# Step 2b (alternative): Run the agent directly as a script (no server)
uv run python -m agent_call.agent
```

### Run the Chat Client (against a running langgraph dev server)

```bash
# Start a new conversation
uv run python -m client_apis.agent_client

# Resume an existing conversation by thread ID
uv run python -m client_apis.agent_client --thread-id <thread_id>
# or short form:
uv run python -m client_apis.agent_client -t <thread_id>
```

### Inspect MCP Tool List

```bash
uv run python -m agent_call.mcp_config    # Prints available tools from all MCP servers
```

> **Note:** There is no Makefile, no `test` command, and no `lint` command defined in this project.

---

## Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      LangGraph Dev Server                      │
│                    (uv run langgraph dev)                       │
│                      localhost:2024                             │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               LangGraph Agent (build_graph)              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │  │
│  │  │  ChatOpenAI  │  │  MCP Tools   │  │  HITL Middle-  │ │  │
│  │  │  (Kimi K2.5) │  │  (dynamic)   │  │  ware          │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘ │  │
│  │              InMemorySaver (checkpointer)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────────┘
                         │ SSE streaming (LangGraph API)
                         ▼
              ┌──────────────────────┐
              │  AgentClient         │
              │  (client_apis/)      │
              │  CLI chat interface  │
              └──────────────────────┘

Agent connects to MCP servers via streamable HTTP:
  ┌──────────────────────────────────────────────────────┐
  │  MultiServerMCPClient (langchain-mcp-adapters)       │
  │                                                      │
  │  "Phone-use" → localhost:8000/mcp  (custom server)   │
  │  "Amap"      → mcp.amap.com/mcp   (Amap Maps API)   │
  └──────────────────────────────────────────────────────┘
           ↑
  ┌────────────────────────┐
  │  custom_mcp_server.py  │  (FastMCP, must be started separately)
  │  Tools:                │
  │    get_gps             │
  │    get_contact_phone   │
  │    make_call           │
  │    send_sms            │
  └────────────────────────┘
```

### Component Map

| File | Role |
|---|---|
| `langgraph.json` | LangGraph CLI config — maps `my_mcp_agent` → `agent_call/agent.py:build_graph` |
| `agent_call/agent.py` | Core agent: loads env, fetches MCP tools, creates `ChatOpenAI` (Kimi), wraps with HITL middleware and `InMemorySaver`, exposes `build_graph()` |
| `agent_call/mcp_config.py` | Creates a `MultiServerMCPClient` connecting to Phone-use and Amap MCP servers |
| `agent_call/middleware.py` | Configures `HumanInTheLoopMiddleware` — defines which tools require approval and what decisions are allowed |
| `agent_call/custom_mcp_server.py` | FastMCP server providing mock phone/GPS tools; runs standalone on port 8000 |
| `client_apis/agent_client.py` | Async aiohttp client for the LangGraph HTTP API; handles SSE streaming, thread management, and interactive HITL resumption |
| `main.py` | Stub entry point (placeholder only) |
| `pyproject.toml` | Dependencies and Python version (`>=3.11`) |
| `.env` / `.env.example` | All secrets and service URLs |

---

## Key Design Patterns

### 1. MCP Tool Discovery at Runtime
The agent fetches its tool list dynamically from MCP servers at startup (`await client.get_tools()`). Tools are not hardcoded — adding a new tool to `custom_mcp_server.py` or connecting a new MCP server in `mcp_config.py` automatically makes it available to the agent.

### 2. Human-in-the-Loop (HITL) Middleware
Sensitive tool calls are gated by `HumanInTheLoopMiddleware`. Each tool can be configured for:
- `True` — user can **approve**, **reject**, or **edit** the tool call
- `{"allowed_decisions": ["approve", "reject"]}` — user can only approve or reject (no edit)

Currently gated tools: `get_gps`, `get_contact_phone`, `send_sms`, `make_call`.

### 3. LangGraph Checkpointing
The agent uses `InMemorySaver` as its checkpointer, enabling multi-turn memory within a session via `thread_id`. For production use, replace with `PostgresSaver`.

### 4. SSE Streaming Client
`AgentClient` (in `client_apis/`) consumes the LangGraph Server's SSE stream, handles both `\n\n` and `\r\n\r\n` delimiters, and progressively prints partial AI responses. After each agent turn, it polls thread state and handles any HITL interrupts interactively.

---

## Configuration Files

### `.env` (required, gitignored)
Copy from `.env.example`. Required keys:

```bash
MOONSHOT_API_KEY=          # Kimi/Moonshot API key (platform.moonshot.cn)
MOONSHOT_BASE_URL=         # https://api.moonshot.cn/v1
MOONSHOT_MODEL=            # kimi-k2-5

AMAP_MCP_KEY=              # Amap Maps MCP key (mcp.amap.com)
AMAP_MCP_URL=              # https://mcp.amap.com/mcp?key=${AMAP_MCP_KEY}

CUSTOM_MCP_URL=            # http://localhost:8000/mcp
CUSTOM_MCP_PORT=           # 8000 (default)

LANGSMITH_API_KEY=         # Optional, for LangSmith tracing
LANGGRAPH_BASE_URL=        # http://localhost:2024 (for the client)
LANGGRAPH_ASSISTANT_ID=    # Auto-generated; query via /assistants/search after first langgraph dev run
```

### `langgraph.json`
Tells the LangGraph CLI which Python function to call to build the agent graph:
```json
{
  "dependencies": ["."],
  "graphs": { "my_mcp_agent": "agent_call/agent.py:build_graph" },
  "env": ".env"
}
```

---

## Startup Order

The custom MCP server **must be running** before starting the agent, because `build_graph()` immediately calls `client.get_tools()` which connects to it.

```bash
# Terminal 1
uv run python -m agent_call.custom_mcp_server

# Terminal 2
uv run langgraph dev

# Terminal 3 (optional: chat client)
uv run python -m client_apis.agent_client
```

After `langgraph dev` first starts, retrieve the assistant ID:
```bash
curl http://localhost:2024/assistants/search | jq '.[0].assistant_id'
# Then set LANGGRAPH_ASSISTANT_ID in .env and update BASE_URL/ASSISTANT_ID in agent_client.py
```
